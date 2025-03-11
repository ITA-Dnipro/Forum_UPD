package repository

import (
	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
)

type QuestionRepository interface {
	CreateQuestion(q *models.Question) error
	GetQuestionByID(id gocql.UUID) (*models.Question, error)
	GetAllQuestions(limit int, pagingState []byte) ([]models.Question, []byte, error)
	GetQuestionsByAuthor(authorID int, limit int, pagingState []byte) ([]models.Question, []byte, error)
	GetQuestionsByStatus(status string, limit int, pagingState []byte) ([]models.Question, []byte, error)
	UpdateQuestion(q *models.Question) error
	DeleteQuestion(id gocql.UUID) error

	SaveQuestion(userID int, questionID gocql.UUID) error
	UnsaveQuestion(userID int, questionID gocql.UUID) error
	GetSavedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error)

	// Optional batch operations (can be implemented later if needed)
	SaveQuestions(userID int, questionIDs []gocql.UUID) error
	UnsaveQuestions(userID int, questionIDs []gocql.UUID) error
}
