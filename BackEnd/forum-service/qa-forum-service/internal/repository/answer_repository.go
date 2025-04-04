package repository

import (
	"fmt"
	"time"

	"github.com/gocql/gocql"

	"github.com/boghtml/qa-forum-service/internal/models"
)

func (db *ScyllaDB) AddAnswer(questionId gocql.UUID, answer *models.QuestionAnswer) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	if answer.ID == (gocql.UUID{}) {
		answer.ID = gocql.TimeUUID()
	}
	answer.CreatedAt = time.Now()
	answer.UpdatedAt = time.Now()
	if answer.Replies == nil {
		answer.Replies = []models.AnswerReply{}
	}
	answer.LikesCount = 0
	answer.DislikesCount = 0

	question.Answers = append(question.Answers, *answer)

	query := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(query, question.Answers, questionId).Exec()
}

func (db *ScyllaDB) UpdateAnswer(questionId gocql.UUID, answerId gocql.UUID, updatedAnswer *models.QuestionAnswer) error {
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
			question.Answers[i].Content = updatedAnswer.Content
			question.Answers[i].UpdatedAt = time.Now()

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

func (db *ScyllaDB) DeleteAnswer(questionId gocql.UUID, answerId gocql.UUID) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionId)
	}

	newAnswers := make([]models.QuestionAnswer, 0, len(question.Answers))
	found := false
	for _, ans := range question.Answers {
		if ans.ID != answerId {
			newAnswers = append(newAnswers, ans)
		} else {
			found = true
		}
	}
	if !found {
		return fmt.Errorf("answer with ID %v not found in question %v", answerId, questionId)
	}

	question.Answers = newAnswers
	query := `UPDATE questions SET answers = ? WHERE question_id = ?`
	return db.session.Query(query, question.Answers, questionId).Exec()
}
