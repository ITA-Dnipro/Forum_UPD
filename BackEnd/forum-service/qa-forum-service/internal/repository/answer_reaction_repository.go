package repository

import (
	"fmt"
	"time"

	"github.com/gocql/gocql"
)

func (db *ScyllaDB) AddAnswerReaction(questionId, answerId gocql.UUID, userID int, isLike bool) error {

	var existingIsLike bool
	checkQuery := `SELECT is_like FROM answer_reactions WHERE question_id = ? AND answer_id = ? AND user_id = ?`
	err := db.session.Query(checkQuery, questionId, answerId, userID).Scan(&existingIsLike)
	if err != gocql.ErrNotFound {
		if err == nil {
			return fmt.Errorf("reaction already exists for user %d on answer %v in question %v", userID, answerId, questionId)
		}
		return err
	}

	createdAt := time.Now()
	reactionQuery := `INSERT INTO answer_reactions (question_id, answer_id, user_id, is_like, created_at) VALUES (?, ?, ?, ?, ?)`
	if err := db.session.Query(reactionQuery, questionId, answerId, userID, isLike, createdAt).Exec(); err != nil {
		return err
	}

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
			if isLike {
				question.Answers[i].LikesCount++
			} else {
				question.Answers[i].DislikesCount++
			}
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}

	updateQuery := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(updateQuery, question.Answers, questionId).Exec()
}

func (db *ScyllaDB) DeleteAnswerReaction(questionId, answerId gocql.UUID, userID int) error {
	var isLike bool
	findQuery := `SELECT is_like FROM answer_reactions WHERE question_id = ? AND answer_id = ? AND user_id = ?`
	if err := db.session.Query(findQuery, questionId, answerId, userID).Scan(&isLike); err != nil {
		if err == gocql.ErrNotFound {
			return fmt.Errorf("reaction not found for user %d on answer %v in question %v", userID, answerId, questionId)
		}
		return err
	}

	deleteQuery := `DELETE FROM answer_reactions WHERE question_id = ? AND answer_id = ? AND user_id = ?`
	if err := db.session.Query(deleteQuery, questionId, answerId, userID).Exec(); err != nil {
		return err
	}

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
			if isLike {
				if question.Answers[i].LikesCount > 0 {
					question.Answers[i].LikesCount--
				}
			} else {
				if question.Answers[i].DislikesCount > 0 {
					question.Answers[i].DislikesCount--
				}
			}
			found = true
			break
		}
	}
	if !found {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}

	updateQuery := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(updateQuery, question.Answers, questionId).Exec()
}
