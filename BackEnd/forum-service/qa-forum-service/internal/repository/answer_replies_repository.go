package repository

import (
	"fmt"
	"time"

	"github.com/gocql/gocql"

	"github.com/boghtml/qa-forum-service/internal/models"
)

func (db *ScyllaDB) AddReply(questionId, answerId gocql.UUID, reply *models.AnswerReply) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	found := false
	for i, ans := range question.Answers {
		if ans.ID == answerId {
			if reply.ID == (gocql.UUID{}) {
				reply.ID = gocql.TimeUUID()
			}
			reply.CreatedAt = time.Now()
			reply.UpdatedAt = time.Now()
			reply.Likes = 0
			reply.Dislikes = 0
			question.Answers[i].Replies = append(question.Answers[i].Replies, *reply)
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}

	query := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(query, question.Answers, questionId).Exec()
}

func (db *ScyllaDB) UpdateReply(questionId, answerId, replyId gocql.UUID, updatedReply *models.AnswerReply) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	foundAnswer := false
	foundReply := false
	for i, ans := range question.Answers {
		if ans.ID == answerId {
			for j, r := range ans.Replies {
				if r.ID == replyId {
					question.Answers[i].Replies[j].Content = updatedReply.Content
					question.Answers[i].Replies[j].UpdatedAt = time.Now()

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

	query := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(query, question.Answers, questionId).Exec()
}

func (db *ScyllaDB) DeleteReply(questionId, answerId, replyId gocql.UUID) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	foundAnswer := false
	foundReply := false
	for i, ans := range question.Answers {
		if ans.ID == answerId {
			newReplies := make([]models.AnswerReply, 0, len(ans.Replies))
			for _, r := range ans.Replies {
				if r.ID != replyId {
					newReplies = append(newReplies, r)
				} else {
					foundReply = true
				}
			}
			question.Answers[i].Replies = newReplies
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

	query := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(query, question.Answers, questionId).Exec()
}
