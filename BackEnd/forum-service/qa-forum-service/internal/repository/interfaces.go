package repository

import (
	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
)

type QuestionRepository interface {
	CreateQuestion(q *models.Question) error
	GetQuestionByID(id gocql.UUID) (*models.Question, error)
	GetAllQuestions() ([]models.Question, error)
	GetQuestionsByAuthor(authorID int) ([]models.Question, error)
	GetQuestionsByStatus(status string) ([]models.Question, error)
	UpdateQuestion(q *models.Question) error
	DeleteQuestion(id gocql.UUID) error

	SaveQuestion(userID int, questionID gocql.UUID) error
	UnsaveQuestion(userID int, questionID gocql.UUID) error
	GetSavedQuestions(userID int) ([]models.Question, error)
}
