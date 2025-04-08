package handlers

import (
	"errors"
	"github.com/gin-gonic/gin"
	"github.com/vladmorozov2/auction-service/internal/models"
	"github.com/vladmorozov2/auction-service/internal/repository"
	"gorm.io/gorm"
	"net/http"
	"time"
)

type Handler struct {
	repo repository.Repository
}

func NewHandler(repo repository.Repository) *Handler {
	return &Handler{repo: repo}
}

func (h *Handler) CreateAuction(c *gin.Context) {
	var auction models.Auction

	if err := c.ShouldBindJSON(&auction); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if auction.StartingBid <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "starting_bid must be greater than 0"})
		return
	}
	if auction.MinBidIncrement != nil && *auction.MinBidIncrement <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "min_bid_increment must be greater than 0"})
		return
	}
	if auction.EndTime.IsZero() {
		c.JSON(http.StatusBadRequest, gin.H{"error": "end_time is required"})
		return
	}
	if auction.EndTime.Before(time.Now()) {
		c.JSON(http.StatusBadRequest, gin.H{"error": "end_time must be in the future"})
		return
	}

	if err := h.repo.CreateAuction(c.Request.Context(), &auction); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to create auction"})
		return
	}

	c.JSON(http.StatusCreated, auction)
}

func (h *Handler) GetOpenAuctions(c *gin.Context) {
	auctions, err := h.repo.GetOpenAuctions(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get open auctions"})
		return
	}

	c.JSON(http.StatusOK, auctions)
}
func (h *Handler) GetAuctionByID(c *gin.Context) {
	id := c.Param("id")

	auction, err := h.repo.GetAuctionByID(c.Request.Context(), id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			c.JSON(http.StatusNotFound, gin.H{"error": "auction not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to retrieve auction"})
		}
		return
	}

	c.JSON(http.StatusOK, auction)
}

type WinnerRequest struct {
	WinnerID int `json:"winner_id"`
}

func (h *Handler) SetAuctionWinner(c *gin.Context) {
	id := c.Param("id")
	

	// Bind JSON to a struct instead of directly to an int
	var req WinnerRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request body"})
		return
	}

	if req.WinnerID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "winner_id must be greater than 0"})
		return
	}

	err := h.repo.SetAuctionWinner(c.Request.Context(), id, req.WinnerID)
	if err != nil {
		switch {
		case errors.Is(err, repository.ErrAuctionNotFound):
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		case errors.Is(err, repository.ErrAuctionAlreadyWon):
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
		case errors.Is(err, repository.ErrAuctionAlreadyClosed):
			c.JSON(http.StatusConflict, gin.H{"error": err.Error()})
		default:
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to set auction winner"})
		}
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "auction winner set successfully"})
}

func (h *Handler) GetAuctionWinnerByID(c *gin.Context) {
	id := c.Param("id")

	auction, err := h.repo.GetAuctionByID(c.Request.Context(), id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			c.JSON(http.StatusNotFound, gin.H{"error": "auction not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to retrieve auction"})
		}
		return
	}

	if auction.WinnerID == nil {
		c.JSON(http.StatusOK, gin.H{"message": "no winner for this auction"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"winner_id": auction.WinnerID})
}
