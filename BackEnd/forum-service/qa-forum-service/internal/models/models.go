package models

import (
	"time"

	"github.com/gocql/gocql"
)

type AnswerReply struct {
	ID         gocql.UUID `json:"id" cql:"id"`
	AuthorID   int        `json:"author_id" cql:"author_id"`
	AuthorName string     `json:"author_name" cql:"author_name"`
	Content    string     `json:"content" cql:"content"`
	CreatedAt  time.Time  `json:"created_at" cql:"created_at"`
	UpdatedAt  time.Time  `json:"updated_at" cql:"updated_at"`
	Likes      int        `json:"likes" cql:"likes"`
	Dislikes   int        `json:"dislikes" cql:"dislikes"`
	ProfileURL string     `json:"profile_url" cql:"profile_url"`
}

type QuestionAnswer struct {
	ID            gocql.UUID    `json:"id" cql:"id"`
	AuthorID      int           `json:"author_id" cql:"author_id"`
	AuthorName    string        `json:"author_name" cql:"author_name"`
	Content       string        `json:"content" cql:"content"`
	CreatedAt     time.Time     `json:"created_at" cql:"created_at"`
	UpdatedAt     time.Time     `json:"updated_at" cql:"updated_at"`
	LikesCount    int           `json:"likes_count" cql:"likes_count"`
	DislikesCount int           `json:"dislikes_count" cql:"dislikes_count"`
	Replies       []AnswerReply `json:"replies,omitempty" cql:"replies"`
	ProfileURL    string        `json:"profile_url" cql:"profile_url"`
}

type Question struct {
	ID             gocql.UUID       `json:"id" cql:"id"`
	AuthorID       int              `json:"author_id" cql:"author_id"`
	Title          string           `json:"title" cql:"title"`
	Description    string           `json:"description" cql:"description"`
	Status         string           `json:"status" cql:"status"`
	ViewsCount     int              `json:"views_count" cql:"views_count"`
	LikesCount     int              `json:"likes_count" cql:"likes_count"`
	DislikesCount  int              `json:"dislikes_count" cql:"dislikes_count"`
	SavesCount     int              `json:"saves_count" cql:"saves_count"`
	Answers        []QuestionAnswer `json:"answers,omitempty" cql:"answers"`
	AcceptedAnswer gocql.UUID       `json:"accepted_answer_id,omitempty" cql:"accepted_answer_id"`
	CreatedAt      time.Time        `json:"created_at" cql:"created_at"`
	UpdatedAt      time.Time        `json:"updated_at" cql:"updated_at"`
	ProfileURL     string           `json:"profile_url" cql:"profile_url"`
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
