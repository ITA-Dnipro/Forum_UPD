package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

func (h *Handler) AddReplyReaction(c *gin.Context) {
	questionId, ok := parseUUIDParam(c, "id")
	if !ok {
		return
	}

	answerId, ok := parseUUIDParam(c, "answerId")
	if !ok {
		return
	}

	replyId, ok := parseUUIDParam(c, "replyId")
	if !ok {
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
	questionId, ok := parseUUIDParam(c, "id")
	if !ok {
		return
	}

	answerId, ok := parseUUIDParam(c, "answerId")
	if !ok {
		return
	}

	replyId, ok := parseUUIDParam(c, "replyId")
	if !ok {
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
