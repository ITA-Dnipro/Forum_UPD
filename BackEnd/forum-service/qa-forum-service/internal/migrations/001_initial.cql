
-- Визначення типу для відповіді на питання
CREATE TYPE IF NOT EXISTS answer_reply (
    id int,
    author_id int,
    author_name text,
    content text,
    created_at timestamp,
    likes int,
    dislikes int,
    profile_url text
);

CREATE TYPE IF NOT EXISTS question_answer (
    id int,
    author_id int,
    author_name text,
    content text,
    created_at timestamp,
    profile_url text,
    likes_count int,      
    dislikes_count int,   
    replies list<frozen<answer_reply>>
);

-- Таблиця для запитань
CREATE TABLE IF NOT EXISTS questions (
    question_id int PRIMARY KEY,
    author_id int,
    title text,
    description text,
    status text,
    views_count int,
    likes_count int,
    dislikes_count int,   
    saves_count int,      
    answers list<frozen<question_answer>>,
    accepted_answer_id int,
    created_at timestamp,
    updated_at timestamp,
    profile_url text 
);

-- Таблиця для індексації за автором
CREATE TABLE IF NOT EXISTS questions_by_author (
    author_id int,
    created_at timestamp,
    question_id int,
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
    question_id int,
    title text,
    author_id int,
    likes_count int,      
    saves_count int,      
    PRIMARY KEY (status, created_at, question_id)
) WITH CLUSTERING ORDER BY (created_at DESC);

-- Таблиця для реакцій до запитань
CREATE TABLE IF NOT EXISTS question_reactions (
    question_id int,
    user_id int,
    is_like boolean,     
    created_at timestamp,
    PRIMARY KEY (question_id, user_id)
);

CREATE TABLE IF NOT EXISTS saved_questions (
    user_id int,
    question_id int,
    saved_at timestamp,
    PRIMARY KEY (user_id, saved_at, question_id)
) WITH CLUSTERING ORDER BY (saved_at DESC);