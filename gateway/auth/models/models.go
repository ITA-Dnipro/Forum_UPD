package models

import "time"

// Role описує роль користувача
type Role struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"unique;not null"`
    Description string
    CreatedAt   time.Time
}

// Permission описує дозвол користувача
type Permission struct {
    ID          uint      `gorm:"primaryKey"`
    Name        string    `gorm:"unique;not null"`
    Description string
    CreatedAt   time.Time
}

// RolePermission зв’язує роль з дозволом (багато-до-багатьох)
type RolePermission struct {
    RoleID       uint `gorm:"primaryKey"`
    PermissionID uint `gorm:"primaryKey"`
}
