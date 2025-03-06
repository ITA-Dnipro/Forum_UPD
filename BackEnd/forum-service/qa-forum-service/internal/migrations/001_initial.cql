-- Визначення типу для відповіді на питання
CREATE TYPE IF NOT EXISTS answer_reply (
    id uuid,
    author_id int,
    content text,
    created_at timestamp,
    updated_at timestamp,
    likes int,
    dislikes int
);

CREATE TYPE IF NOT EXISTS question_answer (
    id uuid,
    author_id int,
    content text,
    created_at timestamp,
    updated_at timestamp,
    likes_count int,
    dislikes_count int,
    replies list<frozen<answer_reply>>
);

-- Таблиця для запитань
CREATE TABLE IF NOT EXISTS questions (
    question_id uuid PRIMARY KEY,
    author_id int,
    title text,
    description text,
    status text,
    likes_count int,
    dislikes_count int,
    saves_count int,
    answers list<frozen<question_answer>>,
    accepted_answer_id uuid,
    created_at timestamp,
    updated_at timestamp
);

-- Таблиця для індексації за автором
CREATE TABLE IF NOT EXISTS questions_by_author (
    author_id int,
    created_at timestamp,
    question_id uuid,
    title text,
    status text,
    likes_count int,
    saves_count int,
    PRIMARY KEY (author_id, created_at, question_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Таблиця для індексації за статусом
CREATE TABLE IF NOT EXISTS questions_by_status (
    status text,
    created_at timestamp,
    question_id uuid,
    title text,
    author_id int,
    likes_count int,
    saves_count int,
    PRIMARY KEY (status, created_at, question_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Таблиця для реакцій до запитань
CREATE TABLE IF NOT EXISTS question_reactions (
    question_id uuid,
    user_id int,
    is_like boolean,
    created_at timestamp,
    PRIMARY KEY (question_id, user_id)
);

CREATE TABLE IF NOT EXISTS saved_questions (
    user_id int,
    question_id uuid,
    saved_at timestamp,
    PRIMARY KEY (user_id, question_id)
);