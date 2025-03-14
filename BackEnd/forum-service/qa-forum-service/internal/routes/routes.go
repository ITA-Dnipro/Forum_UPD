package routes

import (
	"github.com/boghtml/qa-forum-service/internal/handlers"
	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Stub: always skip request
		// In the future, there will be token or session validation here

		/*
					token := c.GetHeader("Authorization")
			        if token == "" {
			            c.JSON(401, gin.H{"error": "Authorization header required"})
			            c.Abort()
			            return
			        }

		*/
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

			question.POST("/reaction", h.AddReaction)
			question.DELETE("/reaction", h.RemoveReaction)

			question.GET("/reactions", h.GetReactions)

			answers := question.Group("/answers")
			{
				answers.POST("", h.CreateAnswer)
				answers.PUT("/:answerId", h.UpdateAnswer)
				answers.DELETE("/:answerId", h.DeleteAnswer)

				answers.POST("/:answerId/accept", h.AcceptAnswer)
				answers.DELETE("/:answerId/accept", h.UnacceptAnswer)

				replies := answers.Group("/:answerId/replies")
				{
					replies.POST("", h.CreateReply)
					replies.PUT("/:replyId", h.UpdateReply)
					replies.DELETE("/:replyId", h.DeleteReply)
				}
			}
		}

		api.GET("/saved-questions", h.GetSavedQuestions)
	}
}
