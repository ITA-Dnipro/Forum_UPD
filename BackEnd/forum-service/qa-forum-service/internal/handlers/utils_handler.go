package handlers

import (
	"fmt"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/gocql/gocql"
)

func parseUUIDParam(c *gin.Context, paramName string) (gocql.UUID, bool) {
	id, err := gocql.ParseUUID(c.Param(paramName))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": fmt.Sprintf("Invalid %s ID", paramName)})
		return gocql.UUID{}, false
	}
	return id, true
}
