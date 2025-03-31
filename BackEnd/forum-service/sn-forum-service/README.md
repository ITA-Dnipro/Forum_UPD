<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S&N Forum Service</title>
</head>
<body>
<h1>S&N Forum Service</h1>
<p>Welcome to the S&N Forum Service, a backend API for a social network forum built with Python (FastAPI) and Apache Cassandra. This project provides a scalable and performant solution for managing blog posts, saved posts, reactions, comments, and more, designed to support a modern social networking platform.</p>

<h2>Table of Contents</h2>
<ul>
    <li><a href="#overview">Project Overview</a></li>
    <li><a href="#features">Features</a></li>
    <li><a href="#technologies">Technologies</a></li>
    <li><a href="#structure">Project Structure</a></li>
    <li><a href="#prerequisites">Prerequisites</a></li>
    <li><a href="#installation">Installation</a></li>
    <li><a href="#running">Running the Application</a></li>
    <li><a href="#endpoints">API Endpoints</a></li>
    <li><a href="#testing">Testing</a></li>
</ul>

<h2 id="overview">Project Overview</h2>
<p>The S&N Forum Service is a RESTful API designed to handle core functionalities of a social network forum. It allows users to create, read, update, and delete posts, save posts for later, react to content (likes/dislikes), and manage comments. The service leverages FastAPI for its high-performance asynchronous capabilities and Cassandra for distributed, scalable data storage.</p>
<p>This project is part of a larger social network ecosystem and serves as the backend for blog-like interactions.</p>

<h2 id="features">Features</h2>
<ul>
    <li><strong>Post Management:</strong> Create, retrieve, update, and delete blog posts with categories, tags, and images.</li>
    <li><strong>Saved Posts:</strong> Allow users to save and unsave posts for later viewing.</li>
    <li><strong>Reactions:</strong> Support for liking and disliking posts and comments.</li>
    <li><strong>Comments:</strong> Add and manage comments and replies on posts.</li>
    <li><strong>Pagination:</strong> Efficiently handle large datasets with paginated responses.</li>
    <li><strong>Swagger UI:</strong> Interactive API documentation available at /docs.</li>
    <li><strong>Asynchronous:</strong> Built with async/await for optimal performance.</li>
    <li><strong>Scalability:</strong> Uses Cassandra for distributed data storage.</li>
</ul>

<h2 id="technologies">Technologies</h2>
<ul>
    <li>Python 3.11: Core programming language.</li>
    <li>FastAPI: High-performance web framework for building APIs with Python.</li>
    <li>Apache Cassandra: Distributed NoSQL database for scalable data storage.</li>
    <li>Pydantic: Data validation and settings management using Python type annotations.</li>
    <li>pytest: Testing framework with support for asynchronous tests.</li>
    <li>Docker: Containerization for consistent development and deployment.</li>
    <li>Cassandra Driver: Python library for interacting with Cassandra.</li>
</ul>

<h2 id="structure">Project Structure</h2>
<pre><code>
sn-forum-service/
├── app/                    # Main application code
│   ├── __init__.py
│   ├── main.py           # FastAPI entry point
│   ├── config.py         # Configuration (e.g., environment variables)
│   ├── routes/           # API routes (endpoints)
│   │   ├── posts.py      # Blog post endpoints
│   │   ├── saved_posts.py # Saved posts endpoints
│   │   ├── comments.py   # Comment endpoints
│   │   ├── categories.py # Category endpoints
│   │   ├── tags.py       # Tag endpoints
│   │   └── ...
│   ├── models/           # Cassandra data models
│   │   ├── post.py
│   │   ├── comment.py
│   │   └── ...
│   ├── services/         # Business logic and database interactions
│   │   ├── cassandra.py  # Cassandra connection and queries
│   ├── schemas/          # Pydantic schemas for request/response validation
│   │   ├── post.py
│   │   ├── pagination.py
│   │   └── ...
│   └── utils/            # Utility scripts
│       ├── migrations.py # Database migrations
│       └── seed_data.py  # Seed initial data
├── tests/                # Unit and integration tests
│   ├── conftest.py       # Test fixtures
│   ├── test_routes/
│   │   ├── test_posts.py
│   │   └── test_saved_posts.py
├── uploads/              # Directory for uploaded files (e.g., images)
├── Dockerfile            # Docker configuration for FastAPI app
├── docker-compose.yml    # Docker Compose for app + Cassandra
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables
├── .gitignore            # Git ignore file
├── pytest.ini            # Pytest configuration
└── README.md             # Project documentation
</code></pre>

<h2 id="prerequisites">Prerequisites</h2>
<ul>
    <li>Python 3.11+: Ensure Python is installed on your system.</li>
    <li>Docker: Required for running the application and Cassandra in containers.</li>
    <li>Git: For cloning the repository.</li>
    <li>pip: Python package manager.</li>
</ul>

<h2 id="installation">Installation</h2>
<h3>Clone the Repository:</h3>
<pre><code>git clone https://github.com/yourusername/sn-forum-service.git
cd sn-forum-service</code></pre>

<h3>Set Up Virtual Environment:</h3>
<pre><code>python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate</code></pre>

<h3>Install Dependencies:</h3>
<pre><code>pip install -r requirements.txt</code></pre>

<h3>Configure Environment Variables:</h3>
<p>Create a `.env` file in the root directory with the following content:</p>
<pre><code># .env
    APP_NAME="Forum MicroService"
    DEBUG=True

    # Cassandra settings

CASSANDRA_CONTACT_POINTS=["cassandra"]
CASSANDRA_KEYSPACE=forum_keyspace
CASSANDRA_PORT=9042
CASSANDRA_USERNAME=cassandra
CASSANDRA_PASSWORD=cassandra

APP_HOST=0.0.0.0
APP_PORT=8000

CORS_ORIGINS=http://localhost

CASSANDRA_MAX_RETRIES=5
CASSANDRA_RETRY_DELAY=5</code></pre>

<h2 id="running">Running the Application</h2>
<h3>Using Docker Compose</h3>
<p>Start the Services:</p>
<pre><code>docker-compose up --build</code></pre>
<p>This will start the FastAPI app and a Cassandra instance in containers.</p>
<p>Access the API:</p>
<ul>
    <li>API: <a href="http://localhost:8000">http://localhost:8000</a></li>
    <li>Swagger UI: <a href="http://localhost:8000/docs">http://localhost:8000/docs</a></li>
</ul>
<p>Stop the Services:</p>
<pre><code>docker-compose down</code></pre>

<h3>Running Locally</h3>
<p>Start Cassandra (if not using Docker): Ensure Cassandra is running locally or on a remote server and update `.env` accordingly.</p>
<p>Run the FastAPI App:</p>
<pre><code>uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload</code></pre>

<h2 id="endpoints">API Endpoints</h2>
<p>Below is a summary of the main endpoints. For full details, explore the interactive Swagger UI at /docs.</p>
<h3>Posts</h3>
<ul>
    <li><strong>POST /api/posts/:</strong> Create a new post.</li>
    <li><strong>GET /api/posts/:</strong> Retrieve a paginated list of posts.</li>
    <li><strong>GET /api/posts/{post_id}:</strong> Retrieve a specific post by ID.</li>
    <li><strong>PUT /api/posts/{post_id}:</strong> Update an existing post.</li>
    <li><strong>DELETE /api/posts/{post_id}:</strong> Delete a post.</li>
    <li><strong>GET /api/posts/by-author/{author_id}:</strong> Retrieve posts by author with pagination.</li>
</ul>
<h3>Saved Posts</h3>
<ul>
    <li><strong>GET /api/saved-posts/:</strong> Retrieve a user's saved posts.</li>
    <li><strong>POST /api/saved-posts/{post_id}/save:</strong> Save a post for a user.</li>
    <li><strong>DELETE /api/saved-posts/{post_id}/unsave:</strong> Unsave a post.</li>
</ul>

<h2 id="testing">Testing</h2>
<p>The project includes unit tests written with pytest to ensure reliability.</p>
<h3>Install Test Dependencies:</h3>
<pre><code>pip install -r requirements.txt</code></pre>
<p>Ensure pytest, pytest-asyncio, httpx, and pytest-mock are installed.</p>
<h3>Run Tests:</h3>
<pre><code>pytest -v</code></pre>
<h3>Test Coverage (optional):</h3>
<p>Install pytest-cov:</p>
<pre><code>pip install pytest-cov</code></pre>
<p>Run with coverage:</p>
<pre><code>pytest --cov=app tests/</code></pre>

## Functionality Testing

To test this functionality, I have provided a link to my collection in Postman:

[Postman Collection](https://educational-platform-7691.postman.co/workspace/SoftServe---work~e04aa574-5147-4873-a9d0-3189be5b56d5/collection/37235075-0e8d87d2-af14-4579-8356-c770cc0e3807?action=share&creator=37235075)


</body>
</html>
