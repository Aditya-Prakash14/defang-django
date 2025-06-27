# E-Learning Platform API Documentation

## Overview
This is a comprehensive E-learning Platform API built with Django REST Framework. The platform supports both instructors and students with features for course management, quizzes, progress tracking, and certificate generation.

## Authentication
The API uses JWT (JSON Web Token) authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Base URL
```
http://localhost:8000/api/
```

## API Endpoints

### Authentication Endpoints (`/api/auth/`)

#### User Registration
- **POST** `/api/auth/register/`
- **Description**: Register a new user (student or instructor)
- **Permissions**: Public
- **Body**:
```json
{
    "username": "string",
    "email": "string",
    "password": "string",
    "password_confirm": "string",
    "first_name": "string",
    "last_name": "string",
    "user_type": "student|instructor",
    "bio": "string (optional)",
    "expertise": "string (optional for instructors)"
}
```

#### User Login
- **POST** `/api/auth/login/`
- **Description**: Login and get JWT tokens
- **Permissions**: Public
- **Body**:
```json
{
    "username": "string",
    "password": "string"
}
```

#### Token Refresh
- **POST** `/api/auth/token/refresh/`
- **Description**: Refresh access token
- **Permissions**: Public
- **Body**:
```json
{
    "refresh": "string"
}
```

#### User Profile
- **GET/PUT/PATCH** `/api/auth/profile/`
- **Description**: Get or update user profile
- **Permissions**: Authenticated

### Course Endpoints (`/api/courses/`)

#### Course Categories
- **GET/POST** `/api/courses/categories/`
- **Description**: List categories or create new (POST requires authentication)
- **Permissions**: Public (GET), Authenticated (POST)

#### Course List
- **GET** `/api/courses/`
- **Description**: List all published courses with filtering
- **Permissions**: Public
- **Query Parameters**:
  - `category`: Filter by category name
  - `difficulty`: Filter by difficulty level
  - `is_free`: Filter free/paid courses
  - `search`: Search in title/description

#### Course Detail
- **GET** `/api/courses/{id}/`
- **Description**: Get course details including lessons
- **Permissions**: Public

#### Course Enrollment
- **POST** `/api/courses/{id}/enroll/`
- **Description**: Enroll in a course
- **Permissions**: Authenticated (Students)

#### Course Lessons
- **GET** `/api/courses/{course_id}/lessons/`
- **Description**: List course lessons
- **Permissions**: Authenticated (Enrolled students or instructor)

#### Mark Lesson Complete
- **POST** `/api/courses/{course_id}/lessons/{lesson_id}/complete/`
- **Description**: Mark a lesson as completed
- **Permissions**: Authenticated (Enrolled students)

#### Course Reviews
- **GET/POST** `/api/courses/{course_id}/reviews/`
- **Description**: List or create course reviews
- **Permissions**: Authenticated (POST requires enrollment)

#### Student Dashboard
- **GET** `/api/courses/dashboard/`
- **Description**: Get student's enrolled courses and progress
- **Permissions**: Authenticated (Students)

#### Student Progress
- **GET** `/api/courses/{course_id}/progress/`
- **Description**: Get detailed progress for a course
- **Permissions**: Authenticated (Enrolled students)

### Instructor Endpoints

#### Instructor Courses
- **GET/POST** `/api/courses/instructor/courses/`
- **Description**: List instructor's courses or create new course
- **Permissions**: Authenticated (Instructors)

#### Instructor Course Management
- **GET/PUT/PATCH/DELETE** `/api/courses/instructor/courses/{id}/`
- **Description**: Manage instructor's course
- **Permissions**: Authenticated (Course instructor)

#### Course Analytics
- **GET** `/api/courses/instructor/courses/{course_id}/analytics/`
- **Description**: Get course analytics and statistics
- **Permissions**: Authenticated (Course instructor)

### Quiz Endpoints (`/api/quizzes/`)

#### Course Quizzes
- **GET/POST** `/api/quizzes/courses/{course_id}/quizzes/`
- **Description**: List course quizzes or create new quiz
- **Permissions**: Authenticated

#### Quiz Detail
- **GET/PUT/PATCH/DELETE** `/api/quizzes/courses/{course_id}/quizzes/{id}/`
- **Description**: Quiz management
- **Permissions**: Authenticated

#### Quiz Questions (Instructor)
- **GET/POST** `/api/quizzes/courses/{course_id}/quizzes/{quiz_id}/questions/`
- **Description**: Manage quiz questions
- **Permissions**: Authenticated (Course instructor)

#### Start Quiz Attempt
- **POST** `/api/quizzes/courses/{course_id}/quizzes/{quiz_id}/start/`
- **Description**: Start a new quiz attempt
- **Permissions**: Authenticated (Enrolled students)

#### Submit Quiz
- **POST** `/api/quizzes/courses/{course_id}/quizzes/{quiz_id}/attempts/{attempt_id}/submit/`
- **Description**: Submit quiz answers
- **Permissions**: Authenticated (Quiz taker)
- **Body**:
```json
{
    "responses": [
        {
            "question": 1,
            "selected_answer": 1,
            "text_answer": "string (for short answer questions)"
        }
    ]
}
```

#### Quiz Attempts
- **GET** `/api/quizzes/courses/{course_id}/quizzes/{quiz_id}/attempts/`
- **Description**: List quiz attempts
- **Permissions**: Authenticated

### Certificate Endpoints (`/api/certificates/`)

#### My Certificates
- **GET** `/api/certificates/my-certificates/`
- **Description**: List student's certificates
- **Permissions**: Authenticated (Students)

#### Generate Certificate
- **POST** `/api/certificates/generate/{course_id}/`
- **Description**: Generate certificate for completed course
- **Permissions**: Authenticated (Students with 100% progress)

#### Download Certificate
- **GET** `/api/certificates/download/{certificate_id}/`
- **Description**: Download certificate PDF
- **Permissions**: Authenticated (Certificate owner)

#### Verify Certificate
- **POST** `/api/certificates/verify/`
- **Description**: Verify a certificate
- **Permissions**: Public
- **Body**:
```json
{
    "certificate_id": "uuid",
    "verification_code": "string"
}
```

#### Public Certificate View
- **GET** `/api/certificates/public/{certificate_id}/`
- **Description**: Public certificate verification
- **Permissions**: Public

## Error Handling

The API uses standard HTTP status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `500`: Internal Server Error

Error responses include a message:
```json
{
    "error": "Error description"
}
```

## Pagination

List endpoints use pagination with the following format:
```json
{
    "count": 100,
    "next": "http://localhost:8000/api/courses/?page=2",
    "previous": null,
    "results": [...]
}
```

## User Types and Permissions

### Students
- Can enroll in courses
- Can view lessons and take quizzes
- Can track progress and receive certificates
- Can review courses

### Instructors
- Can create and manage courses
- Can create lessons and quizzes
- Can view student progress and analytics
- Can see course certificates

### Admin
- Full access to all features
- Can manage users, courses, and system settings
