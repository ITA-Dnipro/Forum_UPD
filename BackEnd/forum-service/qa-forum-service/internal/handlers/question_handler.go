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
	repo repository.Repository
}

func NewHandler(repo repository.Repository) *Handler {
	return &Handler{repo: repo}
}

// @Summary Create a new question
// @Description Creates a new question in the forum
// @Tags Questions
// @Accept json
// @Produce json
// @Param question body models.Question true "Question data"
// @Success 201 {object} models.Question "Created question"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions [post]
func (h *Handler) CreateQuestion(c *gin.Context) {
	var question models.Question
	if err := c.ShouldBindJSON(&question); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if question.Title == "" || question.Description == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Title and Description are required"})
		return
	}
	if question.AuthorID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Author ID must be a positive integer"})
		return
	}

	if err := h.repo.CreateQuestion(&question); err != nil {
		log.Printf("Error creating question: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusCreated, question)
}

// @Summary Get list of questions
// @Description Retrieves a list of questions with optional filters
// @Tags Questions
// @Produce json
// @Param author_id query int false "Filter by author ID"
// @Param status query string false "Filter by status (e.g., open, closed)"
// @Success 200 {array} models.Question "List of questions"
// @Failure 400 {object} map[string]string "Invalid parameters"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions [get]
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

// @Summary Get a question by ID
// @Description Retrieves a specific question by its ID
// @Tags Questions
// @Produce json
// @Param id path string true "Question ID"
// @Success 200 {object} models.Question "Question data"
// @Failure 400 {object} map[string]string "Invalid ID format"
// @Failure 404 {object} map[string]string "Question not found"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id} [get]
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

// @Summary Update a question
// @Description Updates an existing question by its ID
// @Tags Questions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Param question body models.Question true "Updated question data"
// @Success 200 {object} models.Question "Updated question"
// @Failure 400 {object} map[string]string "Invalid request or ID format"
// @Failure 404 {object} map[string]string "Question not found"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id} [put]
func (h *Handler) UpdateQuestion(c *gin.Context) {
	id, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid ID format"})
		return
	}

	question, err := h.repo.GetQuestionByID(id)
	if err != nil {
		log.Printf("Error fetching question %v for update: %v", id, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
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
	if updateData.Title == "" || updateData.Description == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Title and Description are required"})
		return
	}

	question.Title = updateData.Title
	question.Description = updateData.Description
	question.Status = updateData.Status

	if err := h.repo.UpdateQuestion(question); err != nil {
		log.Printf("Error updating question %v: %v", id, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, question)
}

// @Summary Delete a question
// @Description Deletes a question by its ID
// @Tags Questions
// @Produce json
// @Param id path string true "Question ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid ID format"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id} [delete]
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

// @Summary Save a question for a user
// @Description Saves a question to a user's saved list
// @Tags Questions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/save [post]
func (h *Handler) SaveQuestion(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question for save: %v", err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
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
	if saveRequest.UserID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User ID must be a positive integer"})
		return
	}

	if err := h.repo.SaveQuestion(saveRequest.UserID, questionId); err != nil {
		if err.Error() == "question already saved by user" {
			c.JSON(http.StatusConflict, gin.H{"error": "Question already saved"})
			return
		}
		log.Printf("Error saving question %v for user %d: %v", questionId, saveRequest.UserID, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Question saved successfully"})
}

// @Summary Get saved questions for a user
// @Description Retrieves a list of questions saved by a specific user
// @Tags Questions
// @Produce json
// @Param user_id query int true "User ID"
// @Success 200 {array} models.Question "List of saved questions"
// @Failure 400 {object} map[string]string "Invalid user ID"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/saved [get]
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

// @Summary Unsave a question
// @Description Removes a saved question for a user
// @Tags Questions
// @Accept json
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param unsaveRequest body models.UnsaveRequest true "Unsave request body"
// @Success 200 {object} map[string]string "Question unsaved successfully"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/unsave [delete]
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
