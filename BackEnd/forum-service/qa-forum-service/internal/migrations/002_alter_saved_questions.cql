
DROP TABLE saved_questions;

CREATE TABLE IF NOT EXISTS saved_questions (
    user_id int,
    question_id int,
    saved_at timestamp,
    PRIMARY KEY (user_id, question_id)
);