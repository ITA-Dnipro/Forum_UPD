package handlers

import (
	"encoding/hex"
	"log"
	"net/http"
	"strconv"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/boghtml/qa-forum-service/internal/repository"
	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
)

type Handler struct {
	repo *repository.ScyllaDB
}

func NewHandler(repo *repository.ScyllaDB) *Handler {
	return &Handler{repo: repo}
}

func (h *Handler) CreateQuestion(c *gin.Context) {
	var question models.Question
	if err := c.ShouldBindJSON(&question); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.CreateQuestion(&question); err != nil {
		log.Printf("Error creating question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, question)
}

func (h *Handler) GetQuestions(c *gin.Context) {
	authorIDStr := c.Query("author_id")
	status := c.Query("status")
	limitStr := c.Query("limit")
	pagingStateStr := c.Query("paging_state")

	limit, _ := strconv.Atoi(limitStr)
	if limit <= 0 {
		limit = 10
	}
	pagingState, _ := hex.DecodeString(pagingStateStr)

	var questions []models.Question
	var newPagingState []byte
	var err error

	if authorIDStr != "" {
		authorID, err := strconv.Atoi(authorIDStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid author ID format"})
			return
		}
		questions, newPagingState, err = h.repo.GetQuestionsByAuthor(authorID, limit, pagingState)
		if err != nil {
			log.Printf("Error fetching questions by author: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	} else if status != "" {
		questions, newPagingState, err = h.repo.GetQuestionsByStatus(status, limit, pagingState)
		if err != nil {
			log.Printf("Error fetching questions by status: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	} else {
		questions, newPagingState, err = h.repo.GetAllQuestions(limit, pagingState)
		if err != nil {
			log.Printf("Error fetching all questions: %v", err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{
		"questions":    questions,
		"paging_state": hex.EncodeToString(newPagingState),
	})
}

func (h *Handler) GetQuestion(c *gin.Context) {
	id, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	question, err := h.repo.GetQuestionByID(id)
	if err != nil {
		log.Printf("Error fetching question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	c.JSON(http.StatusOK, question)
}

func (h *Handler) UpdateQuestion(c *gin.Context) {
	id, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	question, err := h.repo.GetQuestionByID(id)
	if err != nil {
		log.Printf("Error fetching question for update: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	var updateData models.Question
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	question.Title = updateData.Title
	question.Description = updateData.Description
	question.Status = updateData.Status

	if err := h.repo.UpdateQuestion(question); err != nil {
		log.Printf("Error updating question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, question)
}

func (h *Handler) DeleteQuestion(c *gin.Context) {
	id, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	if err := h.repo.DeleteQuestion(id); err != nil {
		log.Printf("Error deleting question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Question deleted successfully"})
}

func (h *Handler) SaveQuestion(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question for save: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	var saveRequest struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&saveRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.SaveQuestion(saveRequest.UserID, questionId); err != nil {
		if err.Error() == "question already saved by user" {
			c.JSON(http.StatusConflict, gin.H{"error": "Question already saved"})
			return
		}
		log.Printf("Error saving question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Question saved successfully"})
}

func (h *Handler) GetSavedQuestions(c *gin.Context) {
	userIDStr := c.Query("user_id")
	limitStr := c.Query("limit")
	pagingStateStr := c.Query("paging_state")

	userID, err := strconv.Atoi(userIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
		return
	}

	limit, _ := strconv.Atoi(limitStr)
	if limit <= 0 {
		limit = 10
	}
	pagingState, _ := hex.DecodeString(pagingStateStr)

	questions, newPagingState, err := h.repo.GetSavedQuestions(userID, limit, pagingState)
	if err != nil {
		log.Printf("Error fetching saved questions: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"questions":    questions,
		"paging_state": hex.EncodeToString(newPagingState),
	})
}

func (h *Handler) UnsaveQuestion(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question for unsave: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	var unsaveRequest struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&unsaveRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.UnsaveQuestion(unsaveRequest.UserID, questionId); err != nil {
		log.Printf("Error unsaving question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Question unsaved successfully"})
}
