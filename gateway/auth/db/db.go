package db

import (
    "fmt"
    "log"
    "os"
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "github.com/joho/godotenv"
    "github.com/user/forumupd/gateway/auth/models"

)


var DB *gorm.DB

func InitDB() {
    err := godotenv.Load()
    if err != nil {
        log.Println("No .env file found, using system environment variables")
    }

    dbUser := os.Getenv("DB_USER")
    dbPassword := os.Getenv("DB_PASSWORD")
    dbHost := os.Getenv("DB_HOST")
    dbPort := os.Getenv("DB_PORT")
    dbName := os.Getenv("DB_NAME")

    dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%s sslmode=disable",
        dbHost, dbUser, dbPassword, dbName, dbPort)

    DB, err = gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatalf("Error connecting to database: %v", err)
    }

    log.Println("Successfully connected to PostgreSQL!")
}



func SeedOrUpdateDB() {
    // Base Roles in the project
    roles := []models.Role{
        {Name: "AllowAny", Description: "The role for all users even not authenticated"},
        {Name: "IsAuthenticated", Description: "The role for only authenticated users"},
        {Name: "IsStartup", Description: "The role for users who is startup"},
        {Name: "IsInvestor", Description: "The role for users who is investor"},
        {Name: "Admin", Description: "Admin of the system"},
    }

    // Base Permissions in the project
    permissions := []models.Permission{
        {Name: "create:project", Description: "Permission to create new project"},
        {Name: "invest:project", Description: "Permission to invest to new project"},
        {Name: "read:projects", Description: "Permission to read startup projects"},
        {Name: "read:news", Description: "Permission to read news"},
        {Name: "read:events", Description: "Permission to read events"},
        {Name: "create:events", Description: "Permission to create events"},
        {Name: "visit:events", Description: "Permission to visit events"},
        {Name: "create:profile", Description: "Permission to create new profile"},
        {Name: "delete:profile", Description: "Permission to delete new profile"},
        {Name: "read:profile", Description: "Permission to read new profile"},
    }


    rolePerms := map[string][]string{
        "AllowAny":    {"read:projects", "read:events"},

        "IsAuthenticated":    {
        "read:projects",
        "read:news",
        "read:events",
        "create:events",
        "visit:events",
        "create:profile",
        "read:profile",
        },

        "IsStartup":  {
        "create:project",
        "read:news",
        "read:events",
        "create:events",
        "visit:events",
        "create:profile",
        "read:profile",
        },

        "IsInvestor": {
        "invest:project",
        "read:projects",
        "read:news",
        "read:events",
        "create:events",
        "visit:events",
        "create:profile",
        "read:profile"},

        "Admin":    {
        "read:projects",
        "read:news",
        "read:events",
        "create:events",
        "visit:events",
        "create:profile",
        "read:profile",
        "delete:profile",
        },
    }

    for _, r := range roles {
        upsertRole(DB, r)
    }

    for _, p := range permissions {
        upsertPermission(DB, p)
    }

    for roleName, permList := range rolePerms {
        var role models.Role
        if err := DB.Where("name = ?", roleName).First(&role).Error; err != nil {
            log.Printf("Cannot find role %s: %v\n", roleName, err)
            continue
        }
        for _, permName := range permList {
            var perm models.Permission
            if err := DB.Where("name = ?", permName).First(&perm).Error; err != nil {
                log.Printf("Cannot find permission %s: %v\n", permName, err)
                continue
            }
            upsertRolePermission(DB, role.ID, perm.ID)
        }
    }

    log.Println("Seeding/Updating completed!")
}

// upsertRole creates or updates
func upsertRole(db *gorm.DB, newRole models.Role) {
    var existing models.Role
    err := db.Where("name = ?", newRole.Name).First(&existing).Error
    if err != nil {
        if err == gorm.ErrRecordNotFound {
            if err := db.Create(&newRole).Error; err != nil {
                log.Printf("Error creating role %s: %v\n", newRole.Name, err)
            } else {
                log.Printf("Created new role: %s\n", newRole.Name)
            }
        } else {
            log.Printf("Error checking role %s: %v\n", newRole.Name, err)
        }
    } else {
        existing.Description = newRole.Description
        if err := db.Save(&existing).Error; err != nil {
            log.Printf("Error updating role %s: %v\n", newRole.Name, err)
        } else {
            log.Printf("Updated existing role: %s\n", existing.Name)
        }
    }
}

func upsertPermission(db *gorm.DB, newPerm models.Permission) {
    var existing models.Permission
    err := db.Where("name = ?", newPerm.Name).First(&existing).Error
    if err != nil {
        if err == gorm.ErrRecordNotFound {
            if err := db.Create(&newPerm).Error; err != nil {
                log.Printf("Error creating permission %s: %v\n", newPerm.Name, err)
            } else {
                log.Printf("Created new permission: %s\n", newPerm.Name)
            }
        } else {
            log.Printf("Error checking permission %s: %v\n", newPerm.Name, err)
        }
    } else {
        existing.Description = newPerm.Description
        if err := db.Save(&existing).Error; err != nil {
            log.Printf("Error updating permission %s: %v\n", newPerm.Name, err)
        } else {
            log.Printf("Updated existing permission: %s\n", existing.Name)
        }
    }
}

func upsertRolePermission(db *gorm.DB, roleID, permID uint) {
    var rp models.RolePermission
    err := db.Where("role_id = ? AND permission_id = ?", roleID, permID).
        First(&rp).Error

    if err != nil {
        if err == gorm.ErrRecordNotFound {
            rp = models.RolePermission{RoleID: roleID, PermissionID: permID}
            if err := db.Create(&rp).Error; err != nil {
                log.Printf("Error creating role_permission (%d, %d): %v\n", roleID, permID, err)
            } else {
                log.Printf("Created role_permission: role=%d, perm=%d\n", roleID, permID)
            }
        } else {
            log.Printf("Error checking role_permission (%d, %d): %v\n", roleID, permID, err)
        }
    } else {
        // if additional role or permission is created, the new logic must be added
    }
}