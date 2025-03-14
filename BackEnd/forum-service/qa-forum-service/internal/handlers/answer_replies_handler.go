package handlers

import (
	"fmt"
	"log"
	"net/http"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
)

func (h *Handler) CreateReply(c *gin.Context) {
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

	var reply models.AnswerReply
	if err := c.ShouldBindJSON(&reply); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if reply.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Reply content is required"})
		return
	}
	if reply.AuthorID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Author ID must be a positive integer"})
		return
	}

	if err := h.repo.AddReply(questionId, answerId, &reply); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		log.Printf("Error adding reply to answer %v in question %v: %v", answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, reply)
}

func (h *Handler) UpdateReply(c *gin.Context) {
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

	replyId, err := gocql.ParseUUID(c.Param("replyId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reply ID"})
		return
	}

	var updatedReply models.AnswerReply
	if err := c.ShouldBindJSON(&updatedReply); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if updatedReply.Content == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Reply content is required"})
		return
	}

	if err := h.repo.UpdateReply(questionId, answerId, replyId, &updatedReply); err != nil {
		if err.Error() == fmt.Sprintf("answer with ID %v not found in question %v", answerId, questionId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Answer not found"})
			return
		}
		if err.Error() == fmt.Sprintf("reply with ID %v not found in answer %v", replyId, answerId) {
			c.JSON(http.StatusNotFound, gin.H{"error": "Reply not found"})
			return
		}
		log.Printf("Error updating reply %v in answer %v, question %v: %v", replyId, answerId, questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		log.Printf("Error fetching question %v after updating reply: %v", questionId, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}
	for _, ans := range question.Answers {
		if ans.ID == answerId {
			for _, r := range ans.Replies {
				if r.ID == replyId {
					c.JSON(http.StatusOK, r)
					return
				}
			}
		}
	}
	c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to retrieve updated reply"})
}

func (h *Handler) DeleteReply(c *gin.Context) {
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

	replyId, err := gocql.ParseUUID(c.Param("replyId"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid reply ID"})
		return
	}

	if err := h.repo.DeleteReply(questionId, answerId, replyId); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reply deleted successfully"})
}
