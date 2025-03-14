package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gocql/gocql"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gin-gonic/gin"
)

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
