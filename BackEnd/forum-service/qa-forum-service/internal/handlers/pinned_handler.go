package handlers

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
)

func (h *Handler) AcceptAnswer(c *gin.Context) {
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

	var request struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if request.UserID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User ID must be a positive integer"})
		return
	}

	err = h.repo.AcceptAnswer(questionId, answerId, request.UserID)
	if err != nil {
		switch err.Error() {
		case "question not found":
			c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		case "answer not found":
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
		case "only the author can accept an answer":
			c.JSON(http.StatusForbidden, gin.H{"error": "Only the question author can accept an answer"})
		default:
			log.Printf("Error accepting answer %v for question %v by user %d: %v", answerId, questionId, request.UserID, err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Answer accepted successfully"})
}

func (h *Handler) UnacceptAnswer(c *gin.Context) {
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

	var request struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&request); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if request.UserID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "User ID must be a positive integer"})
		return
	}

	err = h.repo.UnacceptAnswer(questionId, answerId, request.UserID)
	if err != nil {
		switch err.Error() {
		case "question not found":
			c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		case "only the author can unaccept an answer":
			c.JSON(http.StatusForbidden, gin.H{"error": "Only the question author can unaccept an answer"})
		default:
			log.Printf("Error unaccepting answer %v for question %v by user %d: %v", answerId, questionId, request.UserID, err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Answer unaccepted successfully"})
}
