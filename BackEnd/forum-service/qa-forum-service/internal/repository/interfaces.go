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

	AddAnswer(questionId gocql.UUID, answer *models.QuestionAnswer) error
	UpdateAnswer(questionId gocql.UUID, answerId gocql.UUID, updatedAnswer *models.QuestionAnswer) error
	DeleteAnswer(questionId gocql.UUID, answerId gocql.UUID) error

	SaveQuestion(userID int, questionID gocql.UUID) error
	UnsaveQuestion(userID int, questionID gocql.UUID) error
	GetSavedQuestions(userID int) ([]models.Question, error)

	AddReaction(userID, questionID gocql.UUID, isLike bool) error
	RemoveReaction(userID, questionID gocql.UUID) error

	GetReactions(questionID gocql.UUID) ([]models.ReactionDetail, error)
	GetLikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error)
	GetDislikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error)

	AddReply(questionId, answerId gocql.UUID, reply *models.AnswerReply) error
	UpdateReply(questionId, answerId, replyId gocql.UUID, updatedReply *models.AnswerReply) error
	DeleteReply(questionId, answerId, replyId gocql.UUID) error

	AddAnswerReaction(questionId, answerId gocql.UUID, userID int, isLike bool) error
	DeleteAnswerReaction(questionId, answerId gocql.UUID, userID int) error

	AddReplyReaction(questionId, answerId, replyId gocql.UUID, userID int, isLike bool) error
	DeleteReplyReaction(questionId, answerId, replyId gocql.UUID, userID int) error

	AcceptAnswer(questionId, answerId gocql.UUID, userID int) error
	UnacceptAnswer(questionId, answerId gocql.UUID, userID int) error
}
