package jwt

import (
    "errors"
    "fmt"
    "strings"

    "github.com/golang-jwt/jwt/v4"
)

var jwtSecret = []byte("mysecret")

func ExtractBearerToken(authHeader string) (string, error) {
    if !strings.HasPrefix(authHeader, "Bearer ") {
        return "", errors.New("invalid Authorization header")
    }
    return strings.TrimPrefix(authHeader, "Bearer "), nil
}

func ParseToken(tokenStr string) (*jwt.Token, error) {
    token, err := jwt.Parse(tokenStr, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return jwtSecret, nil
    })
    if err != nil {
        return nil, err
    }
    return token, nil
}


