package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

// @Summary Add reaction to an answer
// @Description Adds a reaction (like/dislike) to a given answer.
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID (UUID)"
// @Param answerId path string true "Answer ID (UUID)"
// @Success 200 {object} map[string]string "Reaction added successfully"
// @Failure 400 {object} map[string]string "Invalid request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/reaction [post]
func (h *Handler) AddAnswerReaction(c *gin.Context) {
	questionId, ok := parseUUIDParam(c, "id")
	if !ok {
		return
	}

	answerId, ok := parseUUIDParam(c, "answerId")
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

	if err := h.repo.AddAnswerReaction(questionId, answerId, reactionRequest.UserID, reactionRequest.IsLike); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction added successfully"})
}

// @Summary Delete a reaction from an answer
// @Description Removes a user's reaction from a specific answer
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Param answerId path string true "Answer ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID, answer ID, or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/answers/{answerId}/reaction [delete]
func (h *Handler) DeleteAnswerReaction(c *gin.Context) {
	questionId, ok := parseUUIDParam(c, "id")
	if !ok {
		return
	}

	answerId, ok := parseUUIDParam(c, "answerId")
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

	if err := h.repo.DeleteAnswerReaction(questionId, answerId, reactionRequest.UserID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction removed successfully"})
}
