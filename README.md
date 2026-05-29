# Overview

Created a simple FastAPI service to submit and retrieve product feedback. Instead of connecting to a database, the API will temporarily store the data in memory (using a Python list). 

### **Tech Stack**

- **Language:** Python
- **Framework:** FastAPI
- **Validation:** Pydantic
- **Testing:** Pytest

# API Endpoints

<img width="1518" height="427" alt="image" src="https://github.com/user-attachments/assets/bcb5191b-4456-414e-8bbc-fa9bf1ec9238" />


### Health Check - /health

 A simple health check endpoint that returns `{"status": "API is running"}`.

<img width="396" height="250" alt="image" src="https://github.com/user-attachments/assets/4d265a4b-20bd-444c-8764-cf28dccdc280" />


### Get feedback - /feedback (GET)

Retrieves the list of all submitted feedback.

<img width="590" height="571" alt="image" src="https://github.com/user-attachments/assets/ff040262-c646-4a68-9c8c-846a04e18851" />


### Submit feedback - /feedback (POST)

Accepts a JSON payload, validates it against the Pydantic model, and appends it to a global Python list. Returns the created object.

Example input

<img width="303" height="162" alt="image" src="https://github.com/user-attachments/assets/2d14ca8e-cd0a-475e-a6d9-77822cd653ef" />


Example output

<img width="496" height="309" alt="image" src="https://github.com/user-attachments/assets/695baf93-a659-4029-a395-bb54fb1a83b7" />


#### Pydantic model

id: Type - UUID, auto-generated
email: Type - String, must be a valid email format
category: Type - String, restricted to 'Bug', 'Feature', or 'General’
description: Type- String, minimum 10 characters

<img width="296" height="271" alt="image" src="https://github.com/user-attachments/assets/31fd3fa0-9c08-4a3e-af5b-6e98a9ac87fe" />


# Testing with pytest

### Feedback submitted successfully

checks if the feedback is being submitted to the database

<img width="616" height="197" alt="image" src="https://github.com/user-attachments/assets/44ef6463-664d-4120-a9e3-b33c1fea764d" />


### Invalid email

checks if the email is invalid and throws the pydantic schema error

<img width="600" height="164" alt="image" src="https://github.com/user-attachments/assets/f0a54468-1ab0-4c80-8696-976127e87d17" />


### Short Description

checks if the description is shorter then 10 and throws the pydantic schema error

<img width="493" height="167" alt="image" src="https://github.com/user-attachments/assets/0b6dc71f-b9a6-47e4-ac16-e6b2b5d5248b" />


### Get feedback successfully

checks if its returning the list of feedbacks

<img width="640" height="120" alt="image" src="https://github.com/user-attachments/assets/11e7f446-43d5-45e0-8c40-4ec06b82f231" />
