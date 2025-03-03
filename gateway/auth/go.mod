module github.com/user/forumupd/gateway/auth

go 1.24.0

require (
    // Core Authentication & Security
    github.com/golang-jwt/jwt/v4 v4.5.1
    golang.org/x/crypto v0.33.0

    // Environment & Config
    github.com/joho/godotenv v1.5.1

    // Database (PostgreSQL)
    gorm.io/driver/postgres v1.5.11
    gorm.io/gorm v1.25.12

    // Swagger Documentation
    github.com/swaggo/http-swagger v1.3.4
    github.com/swaggo/swag v1.16.4
)

require (
    // Indirect Dependencies (Managed by `go mod tidy`)
    github.com/KyleBanks/depth v1.2.1 // indirect
    github.com/go-openapi/jsonpointer v0.21.0 // indirect
    github.com/go-openapi/jsonreference v0.21.0 // indirect
    github.com/go-openapi/spec v0.21.0 // indirect
    github.com/go-openapi/swag v0.23.0 // indirect
    github.com/jackc/pgpassfile v1.0.0 // indirect
    github.com/jackc/pgservicefile v0.0.0-20221227161230-091c0ba34f0a // indirect
    github.com/jackc/pgx/v5 v5.5.5 // indirect
    github.com/jackc/puddle/v2 v2.2.1 // indirect
    github.com/jinzhu/inflection v1.0.0 // indirect
    github.com/jinzhu/now v1.1.5 // indirect
    github.com/josharian/intern v1.0.0 // indirect
    github.com/mailru/easyjson v0.9.0 // indirect
    github.com/swaggo/files v0.0.0-20220610200504-28940afbdbfe // indirect
    golang.org/x/net v0.35.0 // indirect
    golang.org/x/sync v0.11.0 // indirect
    golang.org/x/text v0.22.0 // indirect
    golang.org/x/tools v0.30.0 // indirect
    gopkg.in/yaml.v3 v3.0.1 // indirect
)
