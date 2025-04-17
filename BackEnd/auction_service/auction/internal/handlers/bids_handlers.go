package handlers

import (
	"errors"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/google/uuid"
	"github.com/vladmorozov2/auction-service/internal/models"
	"github.com/vladmorozov2/auction-service/internal/repository"
)

func (h *Handler) CreateBid(c *gin.Context) {
	auctionIDStr := c.Param("auction_id")
	if auctionIDStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "auction_id is required in URL"})
		return
	}

	auctionID, err := uuid.Parse(auctionIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid auction_id format"})
		return
	}

	var bid models.Bid
	if err := c.ShouldBindJSON(&bid); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid request body"})
		return
	}

	bid.AuctionID = auctionID

	// Minimal validation in handler; repository handles business rules
	if bid.BidAmount <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "bid_amount must be greater than 0"})
		return
	}
	if bid.InvestorID <= 0 {
		c.JSON(http.StatusBadRequest, gin.H{"error": "investor_id must be greater than 0"})
		return
	}

	if err := h.repo.CreateBid(c.Request.Context(), &bid); err != nil {
		if errors.Is(err, repository.ErrAuctionNotFound) {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()}) // Use 400 for validation errors
		}
		return
	}

	c.JSON(http.StatusCreated, bid)
}

func (h *Handler) GetAllBids(c *gin.Context) {
	auctionIDStr := c.Param("auction_id")
	if auctionIDStr == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "auction_id is required in URL"})
		return
	}

	auctionID, err := uuid.Parse(auctionIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid auction_id format"})
		return
	}

	bids, err := h.repo.GetBidsByAuctionID(c.Request.Context(), auctionID.String())
	if err != nil {
		if errors.Is(err, repository.ErrAuctionNotFound) {
			c.JSON(http.StatusNotFound, gin.H{"error": err.Error()})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "failed to get bids"})
		}
		return
	}

	c.JSON(http.StatusOK, bids)
}
