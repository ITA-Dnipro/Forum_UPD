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
        created_at, updated_at, answers
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`

	if err := db.session.Query(mainQuery,
		q.ID, q.AuthorID, q.Title, q.Description, q.Status,
		q.LikesCount, q.DislikesCount, q.SavesCount,
		q.CreatedAt, q.UpdatedAt, q.Answers).Exec(); err != nil {
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
              created_at, updated_at, answers
              FROM questions WHERE question_id = ?`

	if err := db.session.Query(query, id).Scan(
		&q.ID, &q.AuthorID, &q.Title, &q.Description, &q.Status,
		&q.LikesCount, &q.DislikesCount, &q.SavesCount,
		&q.CreatedAt, &q.UpdatedAt, &answers); err != nil {
		if err == gocql.ErrNotFound {
			return nil, nil
		}
		return nil, err
	}

	q.Answers = answers
	return &q, nil
}

func (db *ScyllaDB) GetAllQuestions(limit int, pagingState []byte) ([]models.Question, []byte, error) {
	var questions []models.Question

	query := `SELECT question_id, title, author_id, status, likes_count, saves_count, created_at
              FROM questions_by_status
              WHERE status = ?`

	q := db.session.Query(query, "open").
		PageSize(limit).
		PageState(pagingState)

	iter := q.Iter()

	for {
		var basicInfo struct {
			QuestionID gocql.UUID `cql:"question_id"`
			Title      string     `cql:"title"`
			AuthorID   int        `cql:"author_id"`
			Status     string     `cql:"status"`
			LikesCount int        `cql:"likes_count"`
			SavesCount int        `cql:"saves_count"`
			CreatedAt  time.Time  `cql:"created_at"`
		}
		if !iter.Scan(
			&basicInfo.QuestionID,
			&basicInfo.Title,
			&basicInfo.AuthorID,
			&basicInfo.Status,
			&basicInfo.LikesCount,
			&basicInfo.SavesCount,
			&basicInfo.CreatedAt,
		) {
			break
		}

		fullQuestion, err := db.GetQuestionByID(basicInfo.QuestionID)
		if err == nil && fullQuestion != nil {
			questions = append(questions, *fullQuestion)
		}
	}

	newPagingState := iter.PageState()

	if err := iter.Close(); err != nil {
		return nil, nil, err
	}

	return questions, newPagingState, nil
}

func (db *ScyllaDB) GetQuestionsByAuthor(authorID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	var questions []models.Question

	q := db.session.Query(`SELECT author_id, created_at, question_id, title, status, 
                                  likes_count, saves_count
                           FROM questions_by_author
                           WHERE author_id = ?`,
		authorID).
		PageSize(limit).
		PageState(pagingState)

	iter := q.Iter()

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

		if !iter.Scan(
			&basicInfo.AuthorID,
			&basicInfo.CreatedAt,
			&basicInfo.QuestionID,
			&basicInfo.Title,
			&basicInfo.Status,
			&basicInfo.LikesCount,
			&basicInfo.SavesCount,
		) {
			break
		}

		fullQuestion, err := db.GetQuestionByID(basicInfo.QuestionID)
		if err == nil && fullQuestion != nil {
			questions = append(questions, *fullQuestion)
		}
	}

	newPagingState := iter.PageState()
	if err := iter.Close(); err != nil {
		return nil, nil, err
	}

	return questions, newPagingState, nil
}

func (db *ScyllaDB) GetQuestionsByStatus(status string, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	var questions []models.Question

	q := db.session.Query(`SELECT status, created_at, question_id, title, author_id, 
                                  likes_count, saves_count
                           FROM questions_by_status
                           WHERE status = ?`,
		status).
		PageSize(limit).
		PageState(pagingState)

	iter := q.Iter()

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
		if !iter.Scan(
			&basicInfo.Status,
			&basicInfo.CreatedAt,
			&basicInfo.QuestionID,
			&basicInfo.Title,
			&basicInfo.AuthorID,
			&basicInfo.LikesCount,
			&basicInfo.SavesCount,
		) {
			break
		}

		fullQuestion, err := db.GetQuestionByID(basicInfo.QuestionID)
		if err == nil && fullQuestion != nil && fullQuestion.Status == status {
			questions = append(questions, *fullQuestion)
		}
	}

	newPagingState := iter.PageState()
	if err := iter.Close(); err != nil {
		return nil, nil, err
	}

	return questions, newPagingState, nil
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

	checkQuery := `SELECT user_id FROM saved_questions WHERE user_id = ? AND question_id = ? LIMIT 1`
	iter := db.session.Query(checkQuery, userID, questionID).Iter()
	if iter.NumRows() > 0 {
		iter.Close()
		return fmt.Errorf("question already saved by user")
	}
	if err := iter.Close(); err != nil {
		return err
	}

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

func (db *ScyllaDB) GetSavedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	var questions []models.Question

	q := db.session.Query(`SELECT question_id 
                           FROM saved_questions 
                           WHERE user_id = ?`,
		userID).
		PageSize(limit).
		PageState(pagingState)

	iter := q.Iter()

	var questionID gocql.UUID
	for iter.Scan(&questionID) {
		fullQuestion, err := db.GetQuestionByID(questionID)
		if err == nil && fullQuestion != nil {
			questions = append(questions, *fullQuestion)
		}
	}

	newPagingState := iter.PageState()
	if err := iter.Close(); err != nil {
		return nil, nil, err
	}

	return questions, newPagingState, nil
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
