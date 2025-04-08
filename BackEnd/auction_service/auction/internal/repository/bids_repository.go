package repository

import (
	"context"
	"errors"
	"fmt"
	"time"

	"github.com/google/uuid"
	"github.com/vladmorozov2/auction-service/internal/models"
	"gorm.io/gorm"
)

func (p *PostgreSQL) CreateBid(ctx context.Context, bid *models.Bid) error {
	// Basic field validation
	if bid.AuctionID == uuid.Nil {
		return fmt.Errorf("auction_id cannot be empty")
	}
	if bid.BidAmount <= 0 {
		return fmt.Errorf("bid_amount must be greater than 0")
	}
	if bid.InvestorID <= 0 {
		return fmt.Errorf("investor_id must be greater than 0")
	}

	// Check auction existence and status
	auction, err := p.GetAuctionByID(ctx, bid.AuctionID.String())
	if err != nil {
		if errors.Is(err, ErrAuctionNotFound) {
			return ErrAuctionNotFound
		}
		return fmt.Errorf("failed to verify auction: %w", err)
	}
	if auction.Status != "open" {
		return fmt.Errorf("auction is not open")
	}

	// Validate against starting bid
	if bid.BidAmount < auction.StartingBid {
		return fmt.Errorf("bid_amount %d is less than starting bid %d", bid.BidAmount, auction.StartingBid)
	}

	// Validate against last bid and minimum increment
	lastBid, err := p.GetLastBidForAuction(ctx, bid.AuctionID.String())
	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return fmt.Errorf("failed to check last bid: %w", err)
	}
	if lastBid != nil {
		minIncrement := 100 // Default if nil
		if auction.MinBidIncrement != nil {
			minIncrement = *auction.MinBidIncrement
		}
		if bid.BidAmount < lastBid.BidAmount+minIncrement {
			return fmt.Errorf("bid_amount %d is less than last bid %d plus minimum increment %d", bid.BidAmount, lastBid.BidAmount, minIncrement)
		}
	}

	// Set timestamps and ID
	bid.UpdatedAt = time.Now()
	bid.CreatedAt = time.Now()
	bid.ID = uuid.New()
	return p.db.WithContext(ctx).Create(bid).Error
}

func (p *PostgreSQL) GetLastBidForAuction(ctx context.Context, auctionID string) (*models.Bid, error) {
	var bid models.Bid
	err := p.db.WithContext(ctx).Where("auction_id = ?", auctionID).Order("created_at desc").First(&bid).Error
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, nil // No bids exist, return nil without error
		}
		return nil, fmt.Errorf("failed to get last bid: %w", err)
	}
	return &bid, nil
}

func (p *PostgreSQL) GetBidsByAuctionID(ctx context.Context, auctionID string) ([]*models.Bid, error) {
	// Validate auction existence
	_, err := p.GetAuctionByID(ctx, auctionID)
	if err != nil {
		if errors.Is(err, ErrAuctionNotFound) {
			return nil, ErrAuctionNotFound
		}
		return nil, fmt.Errorf("failed to verify auction: %w", err)
	}

	var bids []*models.Bid
	err = p.db.WithContext(ctx).Where("auction_id = ?", auctionID).Find(&bids).Error
	if err != nil {
		return nil, fmt.Errorf("failed to get bids: %w", err)
	}
	return bids, nil
}
