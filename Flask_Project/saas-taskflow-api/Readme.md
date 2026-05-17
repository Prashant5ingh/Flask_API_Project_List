# SaaS Task Management API
## TaskFlow API 🚀
A production-style SaaS Task Management Backend built using Flask, PostgreSQL, Redis, JWT Authentication, and Docker.
TaskFlow API is a Trello-like backend system that supports organizations, projects, tasks, authentication, role-based access concepts, caching, pagination, rate limiting, and refresh token authentication.
This project demonstrates scalable backend architecture, REST API design, authentication flows, database relationships, and production-ready engineering practices.

## Project URL: https://saas-taskflow-app-production.up.railway.app/api
- https://saas-taskflow-app-production.up.railway.app/api/tasks/health : to check project health.

## ✨ Features
🔐 Authentication & Security
- User Registration
- User Login
- JWT Access Tokens
- Refresh Token Authentication
- Token Revocation (Logout Support)
- Password Hashing
- Protected Routes
- Rate Limiting using Flask-Limiter

## 🏢 Organization & Project Management
- Create Organizations
- Create Projects
- Multi-project architecture
- Project ownership tracking

## 📌 Task Management
- Create Tasks
- Update Tasks
- Delete Tasks
- Task Status Management
- Task Pagination
- Task Search Support (extendable)
- Task Assignment Structure

## 💬 Collaboration
- Task Comments
- User-to-task assignments

## ⚡ Performance Optimization
- Redis Caching
- Cached task listing APIs
- Cache invalidation support

## 🐳 Deployment & DevOps
- Dockerized setup
- Docker Compose support
- PostgreSQL container
- Redis container
- Railway (Backend Deployment Platform)

## 🧠 Tech Stack
Backend
- Python
- Flask
- Flask Blueprint Architecture

## Database
- PostgreSQL
- SQLAlchemy ORM

## Authentication
- JWT (JSON Web Tokens)
- Refresh Tokens
- Token Revocation

## Caching
Redis

## 🔒 Security Features
- JWT authentication
- Refresh token rotation support
- Token revocation
- Werkzeug Password Hashing
- Protected routes
- Flask-Limiter for Rate limiting
- Secure API architecture

## 🗄️ Database Design
Tables
- users
- organizations
- projects
- tasks
- comments
- task_assignments
- refresh_tokens --> For this service table is not created 

## 🔄 Authentication Flow
- Login Flow
- User logs in
- Server validates credentials
- Access token issued (short expiry)
- Refresh token issued (long expiry)

## Refresh Flow
- Client sends refresh token
- Server validates token
- New access token generated

## Logout Flow
- Refresh token revoked
- Token can no longer be used

## ⚡ Redis Caching Strategy

Task listing API responses are cached in Redis.
Cache Flow:
Client Request
      ↓
Flask API
      ↓
Check Redis Cache
      ↓
Cache Hit → Return Cached Data
Cache Miss → Query PostgreSQL → Save in Redis

## 📡 API Endpoints
- Authentication:
- | Method | Endpoint       | Description          |

- | POST   | /auth/register | Register user        |
- | POST   | /auth/login    | Login user           |
- | POST   | /auth/refresh  | Refresh access token |
- | POST   | /auth/logout   | Revoke refresh token |

- Projects
- | Method | Endpoint   | Description    |

- | POST   | /projects | Create project |
- | GET    | /projects/ | Get projects   |

- tasks
- | Method | Endpoint    | Description         |

- | POST   | /tasks     | Create task         |
- | GET    | /tasks/     | Get paginated tasks |
- | PUT    | /tasks/{id} | Update task         |
- | DELETE | /tasks/{id} | Delete task         |


## 🐳 Running with Docker
-- docker-compose up --build

## 🎯 Learning Outcomes
- REST API Development
- Authentication & Authorization
- Database Relationships
- RBAC (Admin / Member roles)
- Backend Architecture
- Caching Strategies
- Docker & DevOps Basics
- Production Backend Engineering

## 🚀 Future Improvements
- Swagger/OpenAPI Documentation
- WebSocket Notifications
- Async Task Queue (Celery)
- Email Notifications
- CI/CD Pipeline
- Kubernetes Deployment
- Unit & Integration Tests

