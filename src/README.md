# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- View who is registered for each activity
- Teacher-only student registration and cancellation

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## Teacher accounts

Teacher accounts are stored in `src/teachers.json`. Passwords are stored as
PBKDF2-SHA256 hashes rather than plain text. To assign a password, generate a
salt and hash from the `src` directory:

```sh
python -c 'import getpass, secrets; from app import hash_teacher_password; salt = secrets.token_hex(16); password = getpass.getpass("Teacher password: "); print({"salt": salt, "password_hash": hash_teacher_password(password, salt)})'
```

Add an entry to the `teachers` array in `src/teachers.json` using the generated
salt and hash, along with the teacher's username:

```json
{
  "teachers": [
    {
      "username": "teacher1",
      "salt": "generated-salt",
      "password_hash": "generated-hash"
    }
  ]
}
```

The browser keeps teacher credentials in memory only until the page is closed or
the teacher logs out. Use HTTPS when the application is accessed over a network.

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| GET    | `/auth/verify`                                                    | Verify teacher credentials                                          |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Teacher-only student registration                                   |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Teacher-only registration cancellation                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

All data is stored in memory, which means data will be reset when the server restarts.
