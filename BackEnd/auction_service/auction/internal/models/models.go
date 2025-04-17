package models

import (
	"github.com/google/uuid"
	"time"
)

type Auction struct {
	ID              uuid.UUID `gorm:"type:uuid;primaryKey" json:"id"`
	StartupID       int       `gorm:"not null;index" json:"startup_id" binding:"required,gt=0"`
	Title           string    `gorm:"size:255;not null" json:"title" binding:"required"`
	Description     *string   `gorm:"type:text" json:"description,omitempty"`
	StartingBid     int       `gorm:"type:int;not null" json:"starting_bid" binding:"required,gt=0"`
	MinBidIncrement *int      `gorm:"type:int;default:100" json:"min_bid_increment,omitempty"`
	Status          string    `gorm:"size:50;check:status IN ('open', 'closed')" json:"status" binding:"required,oneof=open closed"`
	EndTime         time.Time `gorm:"not null" json:"end_time" binding:"required"`
	WinnerID        *int      `gorm:"index" json:"-" binding:"-"`
	CreatedAt       time.Time `json:"-"`
	UpdatedAt       time.Time `json:"-"`
}

// func (l *Auction) BeforeCreate(tx *gorm.DB) (err error) {
// 	l.ID = uuid.New()
// 	if l.CreatedAt.IsZero() {
// 		l.CreatedAt = time.Now()
// 	}
// 	if l.UpdatedAt.IsZero() {
// 		l.UpdatedAt = time.Now()
// 	}
// 	return
// }

type Bid struct {
	ID         uuid.UUID `gorm:"primaryKey" json:"id"`
	AuctionID  uuid.UUID `gorm:"not null;index" json:"auction_id"`
	InvestorID int       `gorm:"not null;index" json:"investor_id"`
	BidAmount  int       `gorm:"type:int;not null" json:"bid_amount"`
	CreatedAt  time.Time `json:"-"`
	UpdatedAt  time.Time `json:"-"`
}
