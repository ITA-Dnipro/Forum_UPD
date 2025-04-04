package repository

import (
	"fmt"
	"time"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
)

func (db *ScyllaDB) AddReaction(userID int, questionID gocql.UUID, isLike bool) error {
	createdAt := time.Now()
	reactionQuery := `INSERT INTO question_reactions (question_id, user_id, is_like, created_at) VALUES (?, ?, ?, ?) IF NOT EXISTS`

	result := make(map[string]interface{})
	applied, err := db.session.Query(reactionQuery, questionID, userID, isLike, createdAt).MapScanCAS(result)
	if err != nil {
		return fmt.Errorf("failed to insert reaction into question_reactions: %v", err)
	}
	if !applied {
		return fmt.Errorf("reaction already exists for user %d on question %v", userID, questionID)
	}

	userReactionQuery := `INSERT INTO question_reactions_by_user (user_id, is_like, question_id, created_at) VALUES (?, ?, ?, ?) IF NOT EXISTS`
	_, err = db.session.Query(userReactionQuery, userID, isLike, questionID, createdAt).MapScanCAS(make(map[string]interface{}))
	if err != nil {
		return fmt.Errorf("failed to insert reaction into question_reactions_by_user: %v", err)
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return fmt.Errorf("failed to get question: %v", err)
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionID)
	}

	if isLike {
		newLikesCount := question.LikesCount + 1
		updateQuery := `UPDATE questions SET likes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newLikesCount, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count: %v", err)
		}

		authorQuery := `UPDATE questions_by_author SET likes_count = ? WHERE author_id = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(authorQuery, newLikesCount, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count in questions_by_author: %v", err)
		}

		statusQuery := `UPDATE questions_by_status SET likes_count = ? WHERE status = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(statusQuery, newLikesCount, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count in questions_by_status: %v", err)
		}
	} else {
		newDislikesCount := question.DislikesCount + 1
		updateQuery := `UPDATE questions SET dislikes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newDislikesCount, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update dislikes count: %v", err)
		}
	}

	return nil
}

func (db *ScyllaDB) RemoveReaction(userID int, questionID gocql.UUID) error {
	var isLike bool
	findQuery := `SELECT is_like FROM question_reactions WHERE question_id = ? AND user_id = ?`
	err := db.session.Query(findQuery, questionID, userID).Scan(&isLike)
	if err != nil {
		if err == gocql.ErrNotFound {
			return fmt.Errorf("reaction not found for user %d on question %v", userID, questionID)
		}
		return fmt.Errorf("failed to check reaction: %v", err)
	}

	deleteQuery := `DELETE FROM question_reactions WHERE question_id = ? AND user_id = ?`
	if err := db.session.Query(deleteQuery, questionID, userID).Exec(); err != nil {
		return fmt.Errorf("failed to delete reaction from question_reactions: %v", err)
	}

	deleteUserQuery := `DELETE FROM question_reactions_by_user WHERE user_id = ? AND is_like = ? AND question_id = ?`
	if err := db.session.Query(deleteUserQuery, userID, isLike, questionID).Exec(); err != nil {
		return fmt.Errorf("failed to delete reaction from question_reactions_by_user: %v", err)
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return fmt.Errorf("failed to get question: %v", err)
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionID)
	}

	if isLike {
		newLikesCount := question.LikesCount - 1
		if newLikesCount < 0 {
			newLikesCount = 0
		}
		updateQuery := `UPDATE questions SET likes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newLikesCount, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count: %v", err)
		}

		authorQuery := `UPDATE questions_by_author SET likes_count = ? WHERE author_id = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(authorQuery, newLikesCount, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count in questions_by_author: %v", err)
		}

		statusQuery := `UPDATE questions_by_status SET likes_count = ? WHERE status = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(statusQuery, newLikesCount, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update likes count in questions_by_status: %v", err)
		}
	} else {
		newDislikesCount := question.DislikesCount - 1
		if newDislikesCount < 0 {
			newDislikesCount = 0
		}
		updateQuery := `UPDATE questions SET dislikes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newDislikesCount, questionID).Exec(); err != nil {
			return fmt.Errorf("failed to update dislikes count: %v", err)
		}
	}

	return nil
}

func (db *ScyllaDB) GetReactions(questionID gocql.UUID) ([]models.ReactionDetail, error) {
	var reactions []models.ReactionDetail
	query := `SELECT user_id, is_like, created_at FROM question_reactions WHERE question_id = ?`
	iter := db.session.Query(query, questionID).Iter()

	var reaction models.ReactionDetail
	for iter.Scan(&reaction.UserID, &reaction.IsLike, &reaction.CreatedAt) {
		reactions = append(reactions, reaction)
	}

	if err := iter.Close(); err != nil {
		return nil, fmt.Errorf("failed to iterate reactions: %v", err)
	}

	return reactions, nil
}

func (db *ScyllaDB) GetQuestionsByReaction(userID int, isLike bool, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	var questions []models.Question

	query := `SELECT question_id FROM question_reactions_by_user WHERE user_id = ? AND is_like = ?`
	iter := db.session.Query(query, userID, isLike).PageSize(limit).PageState(pagingState).Iter()

	var questionID gocql.UUID
	for iter.Scan(&questionID) {
		question, err := db.GetQuestionByID(questionID)
		if err != nil {
			continue
		}
		if question != nil {
			sortAnswers(question)
			questions = append(questions, *question)
		}
	}

	newPagingState := iter.PageState()
	if err := iter.Close(); err != nil {
		return nil, nil, fmt.Errorf("failed to iterate questions: %v", err)
	}

	return questions, newPagingState, nil
}

func (db *ScyllaDB) GetLikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	return db.GetQuestionsByReaction(userID, true, limit, pagingState)
}

func (db *ScyllaDB) GetDislikedQuestions(userID int, limit int, pagingState []byte) ([]models.Question, []byte, error) {
	return db.GetQuestionsByReaction(userID, false, limit, pagingState)
}
