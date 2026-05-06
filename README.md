<!-- README.md -->

# Shopping List Core

The central engine for the AI-Augmented Shopping List. This service acts as the **Persistence Layer**, utilizing a "Git-as-a-DB" pattern to manage shopping data via the GitHub API. Built to be deployed as a Vercel Serverless Function.


## 📥 Cloning the Repository

To begin working with the source code, clone the repository to your local machine:

```bash
git clone https://github.com/LuisAlbertoVasquezVargas/shopping-list-core.git
cd shopping-list-core
```

## 🏗 Repository Structure

```text
.
├── api/
│   └── chat.py       # Vercel Entry Point (Transport Layer)
├── core/
│   └── engine.py     # The Database Engine (Logic Layer)
├── data/
│   └── active_list.json # Local schema reference
├── manage.py         # Project CLI (Development Server)
└── .env              # Environment Configuration
```

## 🚀 Getting Started

### 1. Prerequisites
* Python 3.10+
* A GitHub Personal Access Token (PAT) with `repo` scope.
* A target repository to act as the database.

### 2. Configuration
Create a `.env` file in the root:
```env
GH_TOKEN=your_github_token
GH_OWNER=your_github_username
GH_REPO=shopping-list-db
```

### 3. Running Locally
The project uses a Django-inspired management script for local development:
```bash
python manage.py runserver
```

## 📋 LWC (Last Working Code) Protocol

This project follows the **LWC Protocol** to allow seamless context transfer to LLMs. The following command prunes environment noise and streams the core logic:

```bash
find . -path '*/.*' -prune -o -path '*/venv*' -prune -o -name "*.py" -exec cat {} +
```

## 🔌 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **GET** | `/api/chat` | Fetches the current shopping list. |
| **POST** | `/api/chat` | Adds a new item (`{"item": "name"}`). |
| **PUT** | `/api/chat` | Updates status (`{"id": 1, "status": "bought"}`). |
| **DELETE** | `/api/chat` | Removes an item (`{"id": 1}`). |

