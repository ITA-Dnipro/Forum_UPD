package models

import "time"

type AnswerReply struct {
	ID         int       `json:"id" cql:"id"`
	AuthorID   int       `json:"author_id" cql:"author_id"`
	AuthorName string    `json:"author_name" cql:"author_name"`
	Content    string    `json:"content" cql:"content"`
	CreatedAt  time.Time `json:"created_at" cql:"created_at"`
	Likes      int       `json:"likes" cql:"likes"`
	Dislikes   int       `json:"dislikes" cql:"dislikes"`
	ProfileURL string    `json:"profile_url" cql:"profile_url"`
}

type QuestionAnswer struct {
	ID            int           `json:"id" cql:"id"`
	AuthorID      int           `json:"author_id" cql:"author_id"`
	AuthorName    string        `json:"author_name" cql:"author_name"`
	Content       string        `json:"content" cql:"content"`
	CreatedAt     time.Time     `json:"created_at" cql:"created_at"`
	LikesCount    int           `json:"likes_count" cql:"likes_count"`
	DislikesCount int           `json:"dislikes_count" cql:"dislikes_count"`
	Replies       []AnswerReply `json:"replies" cql:"replies"`
	ProfileURL    string        `json:"profile_url" cql:"profile_url"`
}

type Question struct {
	ID             int              `json:"id"`
	AuthorID       int              `json:"author_id"`
	Title          string           `json:"title"`
	Description    string           `json:"description"`
	Status         string           `json:"status"`
	ViewsCount     int              `json:"views_count"`
	LikesCount     int              `json:"likes_count"`
	DislikesCount  int              `json:"dislikes_count"`
	SavesCount     int              `json:"saves_count"`
	Answers        []QuestionAnswer `json:"answers"`
	AcceptedAnswer int              `json:"accepted_answer_id"`
	CreatedAt      time.Time        `json:"created_at"`
	UpdatedAt      time.Time        `json:"updated_at"`
	ProfileURL     string           `json:"profile_url"`
}

type QuestionReaction struct {
	QuestionID int       `json:"question_id"`
	UserID     int       `json:"user_id"`
	IsLike     bool      `json:"is_like"`
	CreatedAt  time.Time `json:"created_at"`
}

type SavedQuestion struct {
	UserID     int       `json:"user_id"`
	QuestionID int       `json:"question_id"`
	SavedAt    time.Time `json:"saved_at"`
}
