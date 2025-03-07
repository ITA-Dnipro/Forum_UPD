package routes

import (
	"github.com/boghtml/qa-forum-service/internal/handlers"
	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Stub: always skip request
		// In the future, there will be token or session validation here
		c.Next()
	}
}

func SetupRoutes(r *gin.Engine, h *handlers.Handler) {
	api := r.Group("/api/")
	{
		questionsGroup := api.Group("/questions")

		questionsGroup.Use(AuthMiddleware())

		questionsGroup.GET("/", h.GetQuestions)
		questionsGroup.POST("/", h.CreateQuestion)

		question := questionsGroup.Group("/:id")
		{
			question.GET("", h.GetQuestion)
			question.PUT("", h.UpdateQuestion)
			question.DELETE("", h.DeleteQuestion)
			question.POST("/save", h.SaveQuestion)
			question.DELETE("/unsave", h.UnsaveQuestion)
		}
	}

	api.GET("/saved-questions", h.GetSavedQuestions)
}
