package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gocql/gocql"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gin-gonic/gin"
)

// @Summary Create a new answer
// @Description Adds a new answer to a specific question
// @Tags Answers
// @Accept json
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param answer body models.QuestionAnswer true "Answer data"
// @Success 201 {object} models.QuestionAnswer "Created answer"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers [post]
func (h *Handler) CreateAnswer(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question %v for answer creation: %v", questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	var answer models.QuestionAnswer
	if err := c.ShouldBindJSON(&answer); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if answer.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Answer content is required"})
		return
	}
	if answer.AuthorID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Author ID must be a positive integer"})
		return
	}

	if err := h.repo.AddAnswer(questionId, &answer); err != nil {
		log.Printf("Error adding answer to question %v: %v", questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, answer)
}

// @Summary Update an existing answer
// @Description Updates an answer for a specific question
// @Tags Answers
// @Accept json
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param answerId path string true "Answer ID (UUID)"
// @Param answer body models.QuestionAnswer true "Updated answer data"
// @Success 200 {object} models.QuestionAnswer "Updated answer"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId} [put]
func (h *Handler) UpdateAnswer(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	answerId, err := gocql.ParseUUID(c.Param("answerId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid answer ID"})
		return
	}

	var updatedAnswer models.QuestionAnswer
	if err := c.ShouldBindJSON(&updatedAnswer); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if updatedAnswer.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Answer content is required"})
		return
	}

	if err := h.repo.UpdateAnswer(questionId, answerId, &updatedAnswer); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		log.Printf("Error updating answer %v in question %v: %v", answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question %v after updating answer: %v", questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	for _, ans := range question.Answers {
		if ans.ID == answerId {
			c.JSON(http.StatusOK, ans)
			return
		}
	}
	c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated answer"})
}

// @Summary Delete an answer
// @Description Deletes an answer from a specific question
// @Tags Answers
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param answerId path string true "Answer ID (UUID)"
// @Success 200 {object} map[string]string "Answer deleted successfully"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId} [delete]
func (h *Handler) DeleteAnswer(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	answerId, err := gocql.ParseUUID(c.Param("answerId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid answer ID"})
		return
	}

	if err := h.repo.DeleteAnswer(questionId, answerId); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		log.Printf("Error deleting answer %v from question %v: %v", answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Answer deleted successfully"})
}
