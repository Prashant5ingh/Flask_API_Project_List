# SaaS Task Management API
## TaskFlow API 🚀
A production-style SaaS Task Management Backend built using Flask, PostgreSQL, Redis, JWT Authentication, and Docker.
TaskFlow API is a Trello-like backend system that supports organizations, projects, tasks, authentication, role-based access concepts, caching, pagination, rate limiting, and refresh token authentication.
This project demonstrates scalable backend architecture, REST API design, authentication flows, database relationships, and production-ready engineering practices.

## Project URL: https://saas-taskflow-app-production.up.railway.app/api/

## ✨ Features
🔐 Authentication & Security
User Registration
User Login
JWT Access Tokens
Refresh Token Authentication
Token Revocation (Logout Support)
Password Hashing
Protected Routes
Rate Limiting using Flask-Limiter

## 🏢 Organization & Project Management
Create Organizations
Create Projects
Multi-project architecture
Project ownership tracking

## 📌 Task Management
Create Tasks
Update Tasks
Delete Tasks
Task Status Management
Task Pagination
Task Search Support (extendable)
Task Assignment Structure

## 💬 Collaboration
Task Comments
User-to-task assignments

## ⚡ Performance Optimization
Redis Caching
Cached task listing APIs
Cache invalidation support

## 🐳 Deployment & DevOps
Dockerized setup
Docker Compose support
PostgreSQL container
Redis container
Railway (Backend Deployment Platform)

## 🧠 Tech Stack
Backend
Python
Flask
Flask Blueprint Architecture

## Database
PostgreSQL
SQLAlchemy ORM

## Authentication
JWT (JSON Web Tokens)
Refresh Tokens
Token Revocation

## Caching
Redis

## Security
Flask-Limiter
Werkzeug Password Hashing

