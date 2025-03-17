package handlers

import (
	"encoding/hex"
	"log"
	"net/http"
	"strconv"

	"github.com/gocql/gocql"

	"github.com/gin-gonic/gin"
)

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

	reactions, err := h.repo.GetReactions(questionId)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, reactions)
}

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
