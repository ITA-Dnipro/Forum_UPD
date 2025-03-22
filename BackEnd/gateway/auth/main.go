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

    // local packages
    "github.com/user/forumupd/gateway/auth/db"
    "github.com/user/forumupd/gateway/auth/models"
    localjwt "github.com/user/forumupd/gateway/auth/jwt"
    _ "github.com/user/forumupd/gateway/auth/docs"
)

// main initializes the database, sets up HTTP routes, and starts the authorization service.
func main() {
    db.InitDB()

    err := db.DB.AutoMigrate(&models.Role{}, &models.Permission{}, &models.RolePermission{})
    if err != nil {
        log.Fatalf("AutoMigrate failed: %v", err)
    }
    log.Println("Automatic migration completed successfully!")
    db.SeedOrUpdateDB()

	// Setup HTTP route for checking token authorization.
    http.HandleFunc("/check", checkHandler)

    // Swagger documentation which is available on: http://localhost:8080/swagger/index.html
    http.HandleFunc("/swagger/", httpSwagger.WrapHandler)

    log.Println("Authorization service is running on port 8080...")
    log.Fatal(http.ListenAndServe(":8080", nil))
}

// checkHandler validates the JWT token from the request and checks user role permissions.
// checkHandler godoc
// @Summary JWT validation
// @Description Retrieves a JWT token from the Authorization header and optionally checks the user's role.
// @Tags auth
// @Accept  json
// @Produce  json
// @Param Authorization header string true "Bearer <token>"
// @Param requiredRole query string false "Role to check" Enums(Public,NotValidated,IsActive,IsStartup,IsInvestor)
// @Success 200 {string} string "User role: <roleClaim>"
// @Failure 401 {string} string "Missing Authorization header or invalid/expired token"
// @Failure 403 {string} string "Forbidden for this role"
// @Router /check [get]
func checkHandler(w http.ResponseWriter, r *http.Request) {
    authHeader := r.Header.Get("Authorization")
    if authHeader == "" {
    	log.Println("Missing Authorization header in /check request")
        http.Error(w, "Missing Authorization header", http.StatusUnauthorized)
        return
    }

    tokenStr, err := localjwt.ExtractBearerToken(authHeader)
    if err != nil {
    	log.Printf("Error extracting token: %v", err)
        http.Error(w, err.Error(), http.StatusUnauthorized)
        return
    }

    token, claims, err := localjwt.ParseToken(tokenStr)
    if err != nil || !token.Valid {
    	log.Printf("Invalid or expired token: %v", err)
        http.Error(w, "Invalid or expired token", http.StatusUnauthorized)
        return
    }

    roleClaim, ok := claims["role"].(string)
    if !ok {
		log.Println("Missing or invalid 'role' claim")
        http.Error(w, "No or invalid 'role' claim found", http.StatusForbidden)
        return
    }

    // Read the optional query parameter 'requiredRole'
    requiredRole := r.URL.Query().Get("requiredRole")

    // If requiredRole is provided, compare it to the user's role
    if requiredRole != "" {
        // if role in token != requiredRole, returns 403
        if roleClaim != requiredRole {
            http.Error(w, "Forbidden for this role", http.StatusForbidden)
            return
        }
    }

    // If everything is fine, return 200 OK and show the user's role
    w.WriteHeader(http.StatusOK)
    fmt.Fprintf(w, "User role: %s\n", roleClaim)
}
