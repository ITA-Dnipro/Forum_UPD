package repository

import (
	"fmt"
	"time"

	"github.com/gocql/gocql"
)

func (db *ScyllaDB) AddReplyReaction(questionId, answerId, replyId gocql.UUID, userID int, isLike bool) error {
	createdAt := time.Now()
	reactionQuery := `INSERT INTO reply_reactions (question_id, answer_id, reply_id, user_id, is_like, created_at) VALUES (?, ?, ?, ?, ?, ?) IF NOT EXISTS`

	result := make(map[string]interface{})
	applied, err := db.session.Query(reactionQuery, questionId, answerId, replyId, userID, isLike, createdAt).MapScanCAS(result)
	if err != nil {
		return fmt.Errorf("failed to insert reaction: %v", err)
	}
	if !applied {
		return fmt.Errorf("reaction already exists for user %d on reply %v in answer %v, question %v", userID, replyId, answerId, questionId)
	}

	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return fmt.Errorf("failed to get question: %v", err)
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	foundAnswer := false
	foundReply := false
	for i, ans := range question.Answers {
		if ans.ID == answerId {
			for j, reply := range ans.Replies {
				if reply.ID == replyId {
					if isLike {
						question.Answers[i].Replies[j].Likes++
					} else {
						question.Answers[i].Replies[j].Dislikes++
					}
					foundReply = true
					break
				}
			}
			foundAnswer = true
			break
		}
	}
	if !foundAnswer {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}
	if !foundReply {
		return fmt.Errorf("reply with ID %v not found in answer %v", replyId, answerId)
	}

	updateQuery := `UPDATE questions SET answers = ? WHERE question_id = ?`
	if err := db.session.Query(updateQuery, question.Answers, questionId).Exec(); err != nil {
		return fmt.Errorf("failed to update question answers: %v", err)
	}

	return nil
}

func (db *ScyllaDB) DeleteReplyReaction(questionId, answerId, replyId gocql.UUID, userID int) error {
	var isLike bool
	findQuery := `SELECT is_like FROM reply_reactions WHERE question_id = ? AND answer_id = ? AND reply_id = ? AND user_id = ?`
	err := db.session.Query(findQuery, questionId, answerId, replyId, userID).Scan(&isLike)
	if err != nil {
		if err == gocql.ErrNotFound {
			return fmt.Errorf("reaction not found for user %d on reply %v in answer %v, question %v", userID, replyId, answerId, questionId)
		}
		return fmt.Errorf("failed to check reaction: %v", err)
	}

	deleteQuery := `DELETE FROM reply_reactions WHERE question_id = ? AND answer_id = ? AND reply_id = ? AND user_id = ?`
	if err := db.session.Query(deleteQuery, questionId, answerId, replyId, userID).Exec(); err != nil {
		return fmt.Errorf("failed to delete reaction: %v", err)
	}

	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return fmt.Errorf("failed to get question: %v", err)
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	foundAnswer := false
	foundReply := false
	for i, ans := range question.Answers {
		if ans.ID == answerId {
			for j, reply := range ans.Replies {
				if reply.ID == replyId {
					if isLike && question.Answers[i].Replies[j].Likes > 0 {
						question.Answers[i].Replies[j].Likes--
					} else if !isLike && question.Answers[i].Replies[j].Dislikes > 0 {
						question.Answers[i].Replies[j].Dislikes--
					}
					foundReply = true
					break
				}
			}
			foundAnswer = true
			break
		}
	}
	if !foundAnswer {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}
	if !foundReply {
		return fmt.Errorf("reply with ID %v not found in answer %v", replyId, answerId)
	}

	updateQuery := `UPDATE questions SET answers = ? WHERE question_id = ?`
	if err := db.session.Query(updateQuery, question.Answers, questionId).Exec(); err != nil {
		return fmt.Errorf("failed to update question answers: %v", err)
	}

	return nil
}
