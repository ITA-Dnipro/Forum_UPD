package models

import (
	"time"

	"github.com/gocql/gocql"
)

type AnswerReply struct {
	ID        gocql.UUID `json:"id" cql:"id"`
	AuthorID  int        `json:"author_id" cql:"author_id"`
	Content   string     `json:"content" cql:"content"`
	CreatedAt time.Time  `json:"created_at" cql:"created_at"`
	UpdatedAt time.Time  `json:"updated_at" cql:"updated_at"`
	Likes     int        `json:"likes" cql:"likes"`
	Dislikes  int        `json:"dislikes" cql:"dislikes"`
}

type QuestionAnswer struct {
	ID            gocql.UUID    `json:"id" cql:"id"`
	AuthorID      int           `json:"author_id" cql:"author_id"`
	Content       string        `json:"content" cql:"content"`
	CreatedAt     time.Time     `json:"created_at" cql:"created_at"`
	UpdatedAt     time.Time     `json:"updated_at" cql:"updated_at"`
	LikesCount    int           `json:"likes_count" cql:"likes_count"`
	DislikesCount int           `json:"dislikes_count" cql:"dislikes_count"`
	Replies       []AnswerReply `json:"replies,omitempty" cql:"replies"`
	IsAccepted    bool          `json:"is_accepted" cql:"-"`
}

type Question struct {
	ID              gocql.UUID       `json:"id" cql:"id"`
	AuthorID        int              `json:"author_id" cql:"author_id"`
	Title           string           `json:"title" cql:"title"`
	Description     string           `json:"description" cql:"description"`
	Status          string           `json:"status" cql:"status"`
	LikesCount      int              `json:"likes_count" cql:"likes_count"`
	DislikesCount   int              `json:"dislikes_count" cql:"dislikes_count"`
	SavesCount      int              `json:"saves_count" cql:"saves_count"`
	Answers         []QuestionAnswer `json:"answers,omitempty" cql:"answers"`
	AcceptedAnswers []gocql.UUID     `json:"accepted_answer_ids,omitempty" cql:"accepted_answer_ids"`
	CreatedAt       time.Time        `json:"created_at" cql:"created_at"`
	UpdatedAt       time.Time        `json:"updated_at" cql:"updated_at"`
}

type QuestionReaction struct {
	QuestionID gocql.UUID `json:"question_id" cql:"question_id"`
	UserID     int        `json:"user_id" cql:"user_id"`
	IsLike     bool       `json:"is_like" cql:"is_like"`
	CreatedAt  time.Time  `json:"created_at" cql:"created_at"`
}

type SavedQuestion struct {
	UserID     int        `json:"user_id" cql:"user_id"`
	QuestionID gocql.UUID `json:"question_id" cql:"question_id"`
	SavedAt    time.Time  `json:"saved_at" cql:"saved_at"`
}
type ReactionDetail struct {
	UserID    int       `json:"user_id" cql:"user_id"`
	IsLike    bool      `json:"is_like" cql:"is_like"`
	CreatedAt time.Time `json:"created_at" cql:"created_at"`
}

type ReactionRequest struct {
	ReactionType string `json:"reaction_type" example:"like"`
}

type UnsaveRequest struct {
	UserID int `json:"user_id" example:"101"`
}
