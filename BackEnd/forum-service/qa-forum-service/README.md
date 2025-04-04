
<!DOCTYPE  html>

<html  lang="en">

<head>

<meta  charset="UTF-8">

<meta  name="viewport"  content="width=device-width, initial-scale=1.0">

<title>Q&A Forum Service</title>

</head>

<body>

<h1>Q&A Forum Service</h1>

  
<h2>Project Description</h2>

<p>Q&A Forum Service is a RESTful API service for creating, managing, and viewing questions and answers in a forum format. The project is built in the Go programming language, using the Gin web framework to handle HTTP requests, and the ScyllaDB database to store data. The main goal is to provide a fast, scalable, and reliable solution for a Q&A forum similar to Stack Overflow.</p>

<p>The service supports CRUD operations for questions, answers, reactions (likes/dislikes), saving questions by users, as well as pinning and pagination for large data sets.</p>

<h2>Features</h2>

<ul>

<li><strong>Questions:</strong> Create, edit, delete, and view questions with support for filtering by author and status.</li>

<li><strong>Answers:</strong> Add, update, and delete answers to questions.</li>

<li><strong>Reactions:</strong> Likes and dislikes for questions with a count.</li>

<li><strong>Save:</strong> Users can save questions for quick access access.</li>

<li><strong>Pinning:</strong> Authors can pin top answers.</li>

<li><strong>Pagination:</strong> Efficiently process large lists of data using ScyllaDB's paging_state.</li>

</ul>

<h2>Technologies</h2>

<ul>

<li>Go 1.22: A core programming language for server-side logic.</li>

<li>Gin 1.9.1: A lightweight and fast web framework for routing and processing HTTP requests.</li>

<li>ScyllaDB 5.4: A high-performance NoSQL database for scalability and speed.</li>

<li>gocql: A driver for working with ScyllaDB in Go.</li>

<li>testify: A library for writing unit tests and mocks.</li>

<li>httptest: A built-in Go library for testing HTTP endpoints.


</ul>

<h2>Architecture</h2>

<p>The project uses a multi-layered architecture:

<ul>

<li><strong>Handlers:</strong> Processing HTTP requests via Gin, validating input data and returning responses in JSON format.

<li><strong>Repository:</strong> Logic for working with the ScyllaDB database, including CRUD operations and denormalization.

<li><strong>Models:</strong> Data structures for representing entities (questions, answers, reactions).

</ul>

<h2>Denormalization in ScyllaDB</h2>

<p>Denormalization is used to optimize queries:

<ul>

<li><strong>questions:</strong> The main table with full data questions.</li>

<li><strong>questions_by_author:</strong> Table for quick search by author_id.</li>

<li><strong>questions_by_status:</strong> Table for filtering by status (open, closed, etc.).</li>

<li><strong>question_reactions:</strong> Reactions to questions by question_id.</li>

<li><strong>question_reactions_by_user:</strong> Reactions by user_id for quick access.</li>

<li><strong>saved_questions:</strong> Saved questions by users.</li>

</ul>

<h2>Installation and launch</h2>

<h3>Requirements</h3>

<ul>

<li>Go: Version 1.22 or later.</li>

<li>ScyllaDB: Version 5.4 or compatible (can be launched via Docker).</li>

<li>Git: To clone the repository.</li>

</ul>

<h3>Step-by-step instructions</h3>

<p><strong>Cloning the repository:</strong></p>

<pre><code>git clone https://github.com/boghtml/qa-forum-service.git

cd qa-forum-service</code></pre>

<p><strong>Installing dependencies:</strong></p>

<pre><code>go mod tidy</code></pre>

<p><strong>Running ScyllaDB via Docker:</strong></p>

<pre><code>docker run --name scylla -d -p 9042:9042 scylladb/scylla:5.4</code></pre>

<p><strong>Make sure ScyllaDB is running and accessible on localhost:9042.</strong></p>

<p><strong>Configuring the database data:</strong></p>

<p>Create a keyspace and tables (see the "Database Schema" section below).</p>

<p>Use CQL queries via cqlsh or connect via code.</p>

<p><strong>Start the service:</strong></p>

<pre><code>go run main.go</code></pre>

<p>The service will start at http://localhost:8080.</p>

<h2>API endpoints</h2>

<p><strong>Questions</strong></p>

<ul>

<li><strong>POST /api/questions:</strong> Create a new question.</li>

<li><strong>GET /api/questions:</strong> Get a list of questions.</li>

<li><strong>GET /api/questions/:id:</strong> Get a question by ID.


</ul>

<p><strong>Reactions</strong></p>

<ul>

<li><strong>POST /api/questions/:id/reactions:</strong> Like/dislike.

</ul>

<p><strong>Save</strong></p>

<ul>

<li><strong>POST /api/questions/:id/save:</strong> Save question.

</ul>

### Running Tests

To run tests in the root of the project, use the following commands:

1. **Handlers**:
   ```bash
   go test -v ./internal/handlers


2. **Repository**:
   ```bash
   go test -v ./internal/repository


## Functionality Testing

To test this functionality, I have provided a link to my collection in Postman:

[Postman Collection](https://educational-platform-7691.postman.co/workspace/SoftServe---work~e04aa574-5147-4873-a9d0-3189be5b56d5/collection/37235075-0e8d87d2-af14-4579-8356-c770cc0e3807?action=share&creator=37235075)
