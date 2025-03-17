package handlers

import (
	"net/http"

	"github.com/gocql/gocql"

	"github.com/gin-gonic/gin"
)

func (h *Handler) AddReplyReaction(c *gin.Context) {
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

	var reactionRequest struct {
		UserID int  `json:"user_id"`
		IsLike bool `json:"is_like"`
	}
	if err := c.ShouldBindJSON(&reactionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.AddReplyReaction(questionId, answerId, replyId, reactionRequest.UserID, reactionRequest.IsLike); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction added successfully"})
}

func (h *Handler) DeleteReplyReaction(c *gin.Context) {
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

	var reactionRequest struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&reactionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.DeleteReplyReaction(questionId, answerId, replyId, reactionRequest.UserID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction removed successfully"})
}
