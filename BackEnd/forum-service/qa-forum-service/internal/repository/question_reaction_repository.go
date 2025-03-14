package repository

import (
	"fmt"
	"time"

	"github.com/boghtml/qa-forum-service/internal/models"
	"github.com/gocql/gocql"
)

func (db *ScyllaDB) AddReaction(userID int, questionID gocql.UUID, isLike bool) error {
	createdAt := time.Now()

	var existingIsLike bool
	checkQuery := `SELECT is_like FROM question_reactions WHERE question_id = ? AND user_id = ?`
	err := db.session.Query(checkQuery, questionID, userID).Scan(&existingIsLike)
	if err != gocql.ErrNotFound {
		if err == nil {
			return fmt.Errorf("reaction already exists for user %d on question %v", userID, questionID)
		}
		return err
	}

	reactionQuery := `INSERT INTO question_reactions (question_id, user_id, is_like, created_at) VALUES (?, ?, ?, ?)`
	if err := db.session.Query(reactionQuery, questionID, userID, isLike, createdAt).Exec(); err != nil {
		return err
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return err
	}
	if question == nil {
		return fmt.Errorf("question with ID %v not found", questionID)
	}

	if isLike {
		newLikesCount := question.LikesCount + 1
		updateQuery := `UPDATE questions SET likes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newLikesCount, questionID).Exec(); err != nil {
			return err
		}

		authorQuery := `UPDATE questions_by_author SET likes_count = ? 
                        WHERE author_id = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(authorQuery, newLikesCount, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}

		statusQuery := `UPDATE questions_by_status SET likes_count = ? 
                        WHERE status = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(statusQuery, newLikesCount, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}
	} else {
		newDislikesCount := question.DislikesCount + 1
		updateQuery := `UPDATE questions SET dislikes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newDislikesCount, questionID).Exec(); err != nil {
			return err
		}
	}

	return nil
}

func (db *ScyllaDB) RemoveReaction(userID int, questionID gocql.UUID) error {

	var isLike bool
	findQuery := `SELECT is_like FROM question_reactions WHERE question_id = ? AND user_id = ?`
	if err := db.session.Query(findQuery, questionID, userID).Scan(&isLike); err != nil {
		if err == gocql.ErrNotFound {
			return fmt.Errorf("reaction not found for user %d on question %v", userID, questionID)
		}
		return err
	}

	deleteQuery := `DELETE FROM question_reactions WHERE question_id = ? AND user_id = ?`
	if err := db.session.Query(deleteQuery, questionID, userID).Exec(); err != nil {
		return err
	}

	question, err := db.GetQuestionByID(questionID)
	if err != nil {
		return err
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
			return err
		}

		authorQuery := `UPDATE questions_by_author SET likes_count = ? 
                        WHERE author_id = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(authorQuery, newLikesCount, question.AuthorID, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}

		statusQuery := `UPDATE questions_by_status SET likes_count = ? 
                        WHERE status = ? AND created_at = ? AND question_id = ?`
		if err := db.session.Query(statusQuery, newLikesCount, question.Status, question.CreatedAt, questionID).Exec(); err != nil {
			return err
		}
	} else {
		newDislikesCount := question.DislikesCount - 1
		if newDislikesCount < 0 {
			newDislikesCount = 0
		}
		updateQuery := `UPDATE questions SET dislikes_count = ? WHERE question_id = ?`
		if err := db.session.Query(updateQuery, newDislikesCount, questionID).Exec(); err != nil {
			return err
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
		return nil, err
	}

	return reactions, nil
}
