# Mergington High School Activities API

A FastAPI application for extracurricular activity management, teacher sign-in, and announcement publishing.

## Features

- View all available extracurricular activities
- Sign up and unregister students (teacher access)
- Teacher sign-in with session token
- Public announcement banner content driven from MongoDB
- Announcement management (create, update, delete) for signed-in users

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   uvicorn src.app:app --reload
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| GET | `/activities` | Get activities, with optional day/time filtering |
| GET | `/activities/days` | Get all available schedule days |
| POST | `/activities/{activity_name}/signup?email=...&teacher_username=...` | Register a student in an activity |
| POST | `/activities/{activity_name}/unregister?email=...&teacher_username=...` | Remove a student from an activity |
| POST | `/auth/login?username=...&password=...` | Sign in and receive a session token |
| GET | `/auth/check-session` | Validate an existing session (supports Bearer token) |
| GET | `/announcements` | Get active (non-expired) announcements for public display |
| GET | `/announcements/manage` | Get all announcements for management (requires Bearer token) |
| POST | `/announcements` | Create announcement (requires Bearer token) |
| PUT | `/announcements/{announcement_id}` | Update announcement (requires Bearer token) |
| DELETE | `/announcements/{announcement_id}` | Delete announcement (requires Bearer token) |

Announcement payload for `POST /announcements` and `PUT /announcements/{announcement_id}`:

```json
{
   "message": "Spring registration closes Friday.",
   "start_date": "2026-04-14",
   "expiration_date": "2026-04-30"
}
```

- `expiration_date` is required.
- `start_date` is optional.
- Dates must be `YYYY-MM-DD`.

## Data Model

The application stores data in MongoDB:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Teachers** - Uses username as identifier:
   - Display name
   - Role
   - Argon2 password hash

3. **Announcements** - Uses generated announcement IDs:
   - Message
   - Optional start date
   - Required expiration date
   - Created by username

4. **Sessions**:
   - Bearer token
   - Username
   - Expiration timestamp
