package repository

import (
	"fmt"

	"github.com/gocql/gocql"
)

func (db *ScyllaDB) AcceptAnswer(questionId, answerId gocql.UUID, userID int) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question not found")
	}

	if question.AuthorID != userID {
		return fmt.Errorf("only the author can accept an answer")
	}

	answerExists := false
	for _, ans := range question.Answers {
		if ans.ID == answerId {
			answerExists = true
			break
		}
	}
	if !answerExists {
		return fmt.Errorf("answer not found")
	}

	if len(question.AcceptedAnswers) >= 5 {
		return fmt.Errorf("maximum number of accepted answers (5) reached")
	}

	for _, acceptedID := range question.AcceptedAnswers {
		if acceptedID == answerId {
			return nil
		}
	}

	query := `UPDATE questions SET accepted_answer_ids = accepted_answer_ids + ? WHERE question_id = ?`
	return db.session.Query(query, []gocql.UUID{answerId}, questionId).Exec()
}

func (db *ScyllaDB) UnacceptAnswer(questionId, answerId gocql.UUID, userID int) error {
	question, err := db.GetQuestionByID(questionId)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question not found")
	}

	if question.AuthorID != userID {
		return fmt.Errorf("only the author can unaccept an answer")
	}

	acceptedExists := false
	for _, acceptedID := range question.AcceptedAnswers {
		if acceptedID == answerId {
			acceptedExists = true
			break
		}
	}
	if !acceptedExists {
		return nil
	}

	query := `UPDATE questions SET accepted_answer_ids = accepted_answer_ids - ? WHERE question_id = ?`
	return db.session.Query(query, []gocql.UUID{answerId}, questionId).Exec()
}
