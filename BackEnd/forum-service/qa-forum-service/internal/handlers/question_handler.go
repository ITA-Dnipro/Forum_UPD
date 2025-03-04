package handlers

import (
	"github.com/boghtml/qa-forum-service/internal/repository"
)

type Handler struct {
	repo *repository.ScyllaDB
}

func NewHandler(repo *repository.ScyllaDB) *Handler {
	return &Handler{repo: repo}
}
