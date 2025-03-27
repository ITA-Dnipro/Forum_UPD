package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// @Summary Add reaction to a reply
// @Description Adds a reaction (like/dislike) to a given reply.
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param answerId path string true "Answer ID (UUID)"
// @Param replyId path string true "Reply ID (UUID)"
// @Success 200 {object} map[string]string "Reaction added successfully"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/replies/{replyId}/reaction [post]
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

// @Summary Delete a reaction from a reply
// @Description Removes a user's reaction from a specific reply
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Param answerId path string true "Answer ID"
// @Param replyId path string true "Reply ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID, answer ID, reply ID, or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/replies/{replyId}/reaction [delete]
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
