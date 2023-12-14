
---

# API Login - Google CloudRun & Firestore

This repository contains the implementation of the login and registration API for the Culinarix project. The API is built using Flask, deployed on Google CloudRun, and uses Firestore as the database.

## Endpoints

### 1. Register

- **Endpoint:** `/auth/register`
- **Method:** `POST`
- **Description:** Register a new user.
- **Request Body:**
  ```json
  {
    "Email": "user1@gmail.com",
    "Password": "password123",
    "Address": "Bandung",
    "Age": 25,
    "Name": "User Name"
  }
  ```
- **Response:**
  - Success (201):
    ```json
    {
      "message": "User registered successfully!"
    }
    ```
  - Error (400/404):
    ```json
    {
      "message": "Email cannot be empty!",
      -- OR --
      "message": "Email already registered!"
    }
    ```

### 2. Login

- **Endpoint:** `/auth/login`
- **Method:** `POST`
- **Description:** Login with registered credentials.
- **Request Body:**
  ```json
  {
    "Email": "user1@gmail.com",
    "Password": "password123"
  }
  ```
- **Response:**
  - Success (200):
    ```json
    {
      "success": true,
      "message": "Sukses login",
      "data": {
        "User_Id" : "User_Id",
        "token": "JWT_TOKEN"
      }
    }
    ```
  - Error (400/401/404):
    ```json
    {
      "error": "Invalid Email or Password",
      -- OR --
      "error": "User not found",
      -- OR --
      "error": "Invalid Password"
    }
    ```

### 3. Get User Details

- **Endpoint:** `/user/details`
- **Method:** `GET`
- **Description:** Retrieve user details.
- **Request Headers:**
  - `Authorization: Bearer JWT_TOKEN`
- **Response:**
  - Success (200):
    ```json
    {
      "User_Id": 1,
      "Email": "user1@gmail.com",
      "Name": "user Name",
      "Age": 25,
      "Address": "Bandung"
    }
    ```

## Deployment

This API is deployed on Google CloudRun. Ensure you have the necessary environment variables set, including `SECRET_KEY` for token generation.

To run the application locally, use the following command:

```bash
python app.py
```

---
