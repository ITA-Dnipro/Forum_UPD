package handlers

import (
	"encoding/hex"
	"log"
	"net/http"
	"strconv"

	"github.com/gocql/gocql"

	"github.com/gin-gonic/gin"
)

// @Summary Add a reaction to a question
// @Description Adds a like or dislike reaction to a specific question
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/reactions [post]
func (h *Handler) AddReaction(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
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

	if err := h.repo.AddReaction(reactionRequest.UserID, questionId, reactionRequest.IsLike); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction added successfully"})
}

// @Summary Remove a reaction from a question
// @Description Removes a user's reaction from a specific question
// @Tags Reactions
// @Accept json
// @Produce json
// @Param id path string true "Question ID"
// @Success 200 {object} map[string]string "Success message"
// @Failure 400 {object} map[string]string "Invalid question ID or request"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/reactions [delete]
func (h *Handler) RemoveReaction(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	var reactionRequest struct {
		UserID int `json:"user_id"`
	}
	if err := c.ShouldBindJSON(&reactionRequest); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if err := h.repo.RemoveReaction(reactionRequest.UserID, questionId); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Reaction removed successfully"})
}

// @Summary Get reactions for a question
// @Description Retrieves all reactions for a specific question
// @Tags Reactions
// @Produce json
// @Param id path string true "Question ID"
// @Failure 400 {object} map[string]string "Invalid question ID"
// @Failure 404 {object} map[string]string "Question not found"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/{id}/reactions [get]
func (h *Handler) GetReactions(c *gin.Context) {
	questionId, err := gocql.ParseUUID(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid question ID"})
		return
	}

	question, err := h.repo.GetQuestionByID(questionId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	if question == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Question not found"})
		return
	}

	/*
		Future analogue of middleware

		userID, exists := c.Get("user_id")
			if !exists {
				c.JSON(http.StatusUnauthorized, gin.H{"error": "User not authenticated"})
				return
			}

			if userID.(int) != question.AuthorID {
				c.JSON(http.StatusForbidden, gin.H{"error": "Only the question author can view reactions"})
				return
			}
	*/

	reactions, err := h.repo.GetReactions(questionId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, reactions)
}

// @Summary Get liked questions by user
// @Description Retrieves questions liked by a specific user
// @Tags Reactions
// @Produce json
// @Param user_id query int true "User ID"
// @Param limit query int false "Limit number of questions" default(10)
// @Param paging_state query string false "Paging state for pagination"
// @Success 200 {object} map[string]interface{} "Liked questions with paging state"
// @Failure 400 {object} map[string]string "Invalid user ID"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/reactions/liked [get]
func (h *Handler) GetLikedQuestions(c *gin.Context) {
	userIDStr := c.Query("user_id")
	limitStr := c.Query("limit")
	pagingStateStr := c.Query("paging_state")

	userID, err := strconv.Atoi(userIDStr)
	if err != nil || userID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
		return
	}

	limit, _ := strconv.Atoi(limitStr)
	if limit <= 0 {
		limit = 10
	}
	pagingState, _ := hex.DecodeString(pagingStateStr)

	likedQuestions, newPagingState, err := h.repo.GetLikedQuestions(userID, limit, pagingState)
	if err != nil {
		log.Printf("Error fetching liked questions for user %d: %v", userID, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"liked_questions": likedQuestions,
		"paging_state":    hex.EncodeToString(newPagingState),
	})
}

// @Summary Get disliked questions by user
// @Description Retrieves questions disliked by a specific user
// @Tags Reactions
// @Produce json
// @Param user_id query int true "User ID"
// @Param limit query int false "Limit number of questions" default(10)
// @Param paging_state query string false "Paging state for pagination"
// @Success 200 {object} map[string]interface{} "Disliked questions with paging state"
// @Failure 400 {object} map[string]string "Invalid user ID"
// @Failure 500 {object} map[string]string "Server error"
// @Router /api/questions/reactions/disliked [get]
func (h *Handler) GetDislikedQuestions(c *gin.Context) {
	userIDStr := c.Query("user_id")
	limitStr := c.Query("limit")
	pagingStateStr := c.Query("paging_state")

	userID, err := strconv.Atoi(userIDStr)
	if err != nil || userID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
		return
	}

	limit, _ := strconv.Atoi(limitStr)
	if limit <= 0 {
		limit = 10
	}
	pagingState, _ := hex.DecodeString(pagingStateStr)

	dislikedQuestions, newPagingState, err := h.repo.GetDislikedQuestions(userID, limit, pagingState)
	if err != nil {
		log.Printf("Error fetching disliked questions for user %d: %v", userID, err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Internal server error"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"disliked_questions": dislikedQuestions,
		"paging_state":       hex.EncodeToString(newPagingState),
	})
}
