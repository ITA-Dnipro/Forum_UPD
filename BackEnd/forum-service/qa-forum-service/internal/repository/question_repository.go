package repository

import (
	"fmt"
	"time"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
)

func (db *ScyllaDB) CreateQuestion(q *models.Question) error {
	if q.ID == (gocql.UUID{}) {
		q.ID = gocql.TimeUUID()
	}
	q.CreatedAt = time.Now()
	q.UpdatedAt = time.Now()
	if q.Status == "" {
		q.Status = "open"
	}
	if q.Answers == nil {
		q.Answers = []models.QuestionAnswer{}
	}
	q.DislikesCount = 0
	q.SavesCount = 0

	mainQuery := `INSERT INTO questions (
        question_id, author_id, title, description, status, 
        likes_count, dislikes_count, saves_count,
        accepted_answer_id, created_at, updated_at, answers
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	if err := db.session.Query(mainQuery,
		q.ID, q.AuthorID, q.Title, q.Description, q.Status,
		q.LikesCount, q.DislikesCount, q.SavesCount,
		q.AcceptedAnswer, q.CreatedAt, q.UpdatedAt, q.Answers).Exec(); err != nil {
		return err
	}

	authorQuery := `INSERT INTO questions_by_author (
        author_id, created_at, question_id, title, status, likes_count, saves_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?)`

	if err := db.session.Query(authorQuery,
		q.AuthorID, q.CreatedAt, q.ID, q.Title, q.Status, q.LikesCount, q.SavesCount).Exec(); err != nil {
		return fmt.Errorf("error inserting into questions_by_author table: %w", err)
	}

	statusQuery := `INSERT INTO questions_by_status (
        status, created_at, question_id, title, author_id, likes_count, saves_count
    ) VALUES (?, ?, ?, ?, ?, ?, ?)`

	if err := db.session.Query(statusQuery,
		q.Status, q.CreatedAt, q.ID, q.Title, q.AuthorID, q.LikesCount, q.SavesCount).Exec(); err != nil {
		return fmt.Errorf("error inserting into questions_by_status table: %w", err)
	}

	return nil
}
func (db *ScyllaDB) GetQuestionByID(id gocql.UUID) (*models.Question, error) {
	var q models.Question
	var answers []models.QuestionAnswer

	query := `SELECT question_id, author_id, title, description, status, 
              likes_count, dislikes_count, saves_count,
              accepted_answer_id, created_at, updated_at, answers
              FROM questions WHERE question_id = ?`

	if err := db.session.Query(query, id).Scan(
		&q.ID, &q.AuthorID, &q.Title, &q.Description, &q.Status,
		&q.LikesCount, &q.DislikesCount, &q.SavesCount,
		&q.AcceptedAnswer, &q.CreatedAt, &q.UpdatedAt, &answers); err != nil {
		if err == gocql.ErrNotFound {
			return nil, nil
		}
		return nil, err
	}

	q.Answers = answers
	return &q, nil
}

func (db *ScyllaDB) GetAllQuestions() ([]models.Question, error) {
	var questions []models.Question

	query := `SELECT question_id, author_id, title, description, status, 
              likes_count, dislikes_count, saves_count,
              accepted_answer_id, created_at, updated_at, answers
              FROM questions`

	iter := db.session.Query(query).Iter()
	var q models.Question
	var answers []models.QuestionAnswer
	for iter.Scan(
		&q.ID, &q.AuthorID, &q.Title, &q.Description, &q.Status,
		&q.LikesCount, &q.DislikesCount, &q.SavesCount,
		&q.AcceptedAnswer, &q.CreatedAt, &q.UpdatedAt, &answers) {
		q.Answers = answers
		questions = append(questions, q)
	}
	return questions, iter.Close()
}
func (db *ScyllaDB) GetQuestionsByAuthor(authorID int) ([]models.Question, error) {
	var questions []models.Question

	query := `SELECT author_id, created_at, question_id, title, status, likes_count, saves_count
             FROM questions_by_author 
             WHERE author_id = ?`

	iter := db.session.Query(query, authorID).Iter()
	for {
		var basicInfo struct {
			AuthorID   int        `cql:"author_id"`
			CreatedAt  time.Time  `cql:"created_at"`
			QuestionID gocql.UUID `cql:"question_id"`
			Title      string     `cql:"title"`
			Status     string     `cql:"status"`
			LikesCount int        `cql:"likes_count"`
			SavesCount int        `cql:"saves_count"`
		}
		if !iter.Scan(&basicInfo.AuthorID, &basicInfo.CreatedAt, &basicInfo.QuestionID,
			&basicInfo.Title, &basicInfo.Status, &basicInfo.LikesCount, &basicInfo.SavesCount) {
			break
		}

		fullQuestion, err := db.GetQuestionByID(basicInfo.QuestionID)
		if err == nil && fullQuestion != nil {
			questions = append(questions, *fullQuestion)
		}
	}
	if err := iter.Close(); err != nil {
		return nil, err
	}
	return questions, nil
}

func (db *ScyllaDB) GetQuestionsByStatus(status string) ([]models.Question, error) {
	var questions []models.Question

	query := `SELECT status, created_at, question_id, title, author_id, likes_count, saves_count
             FROM questions_by_status 
             WHERE status = ?`

	iter := db.session.Query(query, status).Iter()
	for {
		var basicInfo struct {
			Status     string     `cql:"status"`
			CreatedAt  time.Time  `cql:"created_at"`
			QuestionID gocql.UUID `cql:"question_id"`
			Title      string     `cql:"title"`
			AuthorID   int        `cql:"author_id"`
			LikesCount int        `cql:"likes_count"`
			SavesCount int        `cql:"saves_count"`
		}
		if !iter.Scan(&basicInfo.Status, &basicInfo.CreatedAt, &basicInfo.QuestionID,
			&basicInfo.Title, &basicInfo.AuthorID, &basicInfo.LikesCount, &basicInfo.SavesCount) {
			break
		}

		fullQuestion, err := db.GetQuestionByID(basicInfo.QuestionID)
		if err == nil && fullQuestion != nil && fullQuestion.Status == status {
			questions = append(questions, *fullQuestion)
		}
	}
	if err := iter.Close(); err != nil {
		return nil, err
	}
	return questions, nil
}
func (db *ScyllaDB) UpdateQuestion(q *models.Question) error {
	q.UpdatedAt = time.Now()

	query := `UPDATE questions 
             SET title = ?, description = ?, status = ?, updated_at = ?, 
             likes_count = ?, dislikes_count = ?, saves_count = ?
             WHERE question_id = ?`

	if err := db.session.Query(query,
		q.Title, q.Description, q.Status, q.UpdatedAt,
		q.LikesCount, q.DislikesCount, q.SavesCount, q.ID).Exec(); err != nil {
		return err
	}

	authorQuery := `UPDATE questions_by_author 
                   SET likes_count = ?, saves_count = ? 
                   WHERE author_id = ? AND created_at = ? AND question_id = ?`
	if err := db.session.Query(authorQuery,
		q.LikesCount, q.SavesCount, q.AuthorID, q.CreatedAt, q.ID).Exec(); err != nil {
		return err
	}

	statusQuery := `UPDATE questions_by_status 
                   SET likes_count = ?, saves_count = ? 
                   WHERE status = ? AND created_at = ? AND question_id = ?`
	if err := db.session.Query(statusQuery,
		q.LikesCount, q.SavesCount, q.Status, q.CreatedAt, q.ID).Exec(); err != nil {
		return err
	}

	return nil
}

func (db *ScyllaDB) DeleteQuestion(id gocql.UUID) error {
	query := `DELETE FROM questions WHERE question_id = ?`
	return db.session.Query(query, id).Exec()
}

func (db *ScyllaDB) SaveQuestion(userID int, questionID gocql.UUID) error {
	savedAt := time.Now()

	saveQuery := `INSERT INTO saved_questions (user_id, question_id, saved_at) VALUES (?, ?, ?)`
	if err := db.session.Query(saveQuery, userID, questionID, savedAt).Exec(); err != nil {
		return err
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return err
	}
	if question != nil {
		updateQuery := `UPDATE questions SET saves_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, question.SavesCount+1, questionID).Exec(); err != nil {
			return err
		}

		authorQuery := `UPDATE questions_by_author SET saves_count = ? 
                        WHERE author_id = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(authorQuery, question.SavesCount+1, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}

		statusQuery := `UPDATE questions_by_status SET saves_count = ? 
                        WHERE status = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(statusQuery, question.SavesCount+1, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}
	}

	return nil
}

func (db *ScyllaDB) GetSavedQuestions(userID int) ([]models.Question, error) {
	var questions []models.Question

	query := `SELECT question_id FROM saved_questions WHERE user_id = ?`
	iter := db.session.Query(query, userID).Iter()

	var questionID gocql.UUID
	for iter.Scan(&questionID) {
		if question, err := db.GetQuestionByID(questionID); err == nil && question != nil {
			questions = append(questions, *question)
		}
	}
	if err := iter.Close(); err != nil {
		return nil, err
	}

	return questions, nil
}

func (db *ScyllaDB) UnsaveQuestion(userID int, questionID gocql.UUID) error {
	deleteQuery := `DELETE FROM saved_questions WHERE user_id = ? AND question_id = ?`
	if err := db.session.Query(deleteQuery, userID, questionID).Exec(); err != nil {
		return err
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question not found")
	}

	newSavesCount := question.SavesCount - 1
	if newSavesCount < 0 {
		newSavesCount = 0
	}

	updateQuery := `UPDATE questions SET saves_count = ? WHERE question_id = ?`
	if err := db.session.Query(updateQuery, newSavesCount, questionID).Exec(); err != nil {
		return err
	}

	authorQuery := `UPDATE questions_by_author SET saves_count = ? 
                    WHERE author_id = ? AND created_at = ? AND question_id = ?`
	if err := db.session.Query(authorQuery, newSavesCount, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
		return err
	}

	statusQuery := `UPDATE questions_by_status SET saves_count = ? 
                    WHERE status = ? AND created_at = ? AND question_id = ?`
	if err := db.session.Query(statusQuery, newSavesCount, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
		return err
	}

	return nil
}
