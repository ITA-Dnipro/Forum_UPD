// @title        Authorization Service API
// @version      1.0
// @description  This service provides validation JWT-token
// @BasePath     /

package main

import (
    "fmt"
    "log"
    "net/http"

    httpSwagger "github.com/swaggo/http-swagger"

    "github.com/user/forumupd/gateway/auth/db"
    "github.com/user/forumupd/gateway/auth/models"
    localjwt "github.com/user/forumupd/gateway/auth/jwt"
    _ "github.com/user/forumupd/gateway/auth/docs"
)

func main() {
    db.InitDB()

    err := db.DB.AutoMigrate(&models.Role{}, &models.Permission{}, &models.RolePermission{})
    if err != nil {
        log.Fatalf("AutoMigrate failed: %v", err)
    }
    log.Println("Automatic migration completed successfully!")
    db.SeedOrUpdateDB()

    // The route is used for checking token /check
    http.HandleFunc("/check", checkHandler)

    // Swagger documentation which is available on: http://localhost:8080/swagger/index.html
    http.HandleFunc("/swagger/", httpSwagger.WrapHandler)

    log.Println("Authorization service is running on port 8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

// checkHandler godoc
// @Summary Checking JWT
// @Description Get JWT-token from header and check the user's role
// @Tags auth
// @Accept  json
// @Produce  json
// @Param Authorization header string true "Bearer <token>"
// @Success 200 {string} string "User role: IsStartup  / IsInvestor / Both"
// @Failure 401 {string} string "Missing Authorization header / Invalid or expired token"
// @Failure 403 {string} string "No or invalid 'role' claim found / Unknown role"
// @Router /check [get]
func checkHandler(w http.ResponseWriter, r *http.Request) {
    authHeader := r.Header.Get("Authorization")
    if authHeader == "" {
        http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
        return
    }

    tokenStr, err := localjwt.ExtractBearerToken(authHeader)
    if err != nil {
        http.Error(w, err.Error(), http.StatusUnauthorized)
        return
    }

    token, claims, err := localjwt.ParseToken(tokenStr)
    if err != nil || !token.Valid {
        http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
        return
    }

    roleClaim, ok := claims["role"].(string)
    if !ok {
        http.Error(w, "No or invalid 'role' claim found", http.StatusForbidden)
        return
    }

    switch roleClaim {
    case "IsStartup":
        fmt.Fprintln(w, "User role: IsStartup")
    case "IsInvestor":
        fmt.Fprintln(w, "User role: IsInvestor")
    case "Both":
        fmt.Fprintln(w, "User roles: IsStartup and IsInvestor")
    default:
        http.Error(w, "Unknown role", http.StatusForbidden)
    }
}

