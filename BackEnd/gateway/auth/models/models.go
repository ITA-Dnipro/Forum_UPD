package models

import (
    "time"
    "gorm.io/gorm"
)

type Permission struct {
    gorm.Model
    Name        string    `gorm:"unique;not null"`
    Description string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    DeletedAt   gorm.DeletedAt
}

type Role struct {
    gorm.Model
    Name        string    `gorm:"size:255;not null"`
    Description string
    CreatedAt   time.Time
    UpdatedAt   time.Time
    DeletedAt   gorm.DeletedAt
}

type RolePermission struct {
    gorm.Model
    RoleID       uint `gorm:"foreignKey"`
    PermissionID uint `gorm:"foreignKey"`
}

func GetUserRoles(db *gorm.DB, _ string) ([]string, error) {
    var roles []Role
    if err := db.Find(&roles).Error; err != nil {
        return nil, err
    }

    var roleNames []string
    for _, role := range roles {
        roleNames = append(roleNames, role.Name)
    }
    return roleNames, nil
}
