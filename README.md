
# shopping-list-core

The serverless backend "engine" for a chat-driven shopping list. This repository contains the Python-based logic that processes user input and manages persistence within the `shopping-list-db` repository.

## 🏗 Architecture
This project serves as the **Middleware Layer** in a three-tier modular system:
1. **`shopping-list-ui`**: (Frontend) Minimalist chat interface.
2. **`shopping-list-core`**: (This repo) Python Vercel functions for intent parsing and DB communication.
3. **`shopping-list-db`**: (Database) Private GitHub repository storing JSON data and chat history.

## 🛠 Tech Stack
* **Language:** Python
* **Deployment:** Vercel (Serverless Functions)
* **API Wrapper:** [PyGithub](https://github.com/PyGithub/PyGithub)
* **Data Store:** GitHub REST API (Git-as-a-DB)

## 🚀 Setup & Installation

### Local Development
1. Clone the repository:
   ```bash
   git clone https://github.com/LuisAlbertoVasquezVargas/shopping-list-core.git
   cd shopping-list-core
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Vercel Deployment
1. Connect this repository to a new project in the **Vercel Dashboard**.
2. Configure the following **Environment Variables**:
   * `GH_TOKEN`: Your GitHub Personal Access Token.
   * `GH_OWNER`: `LuisAlbertoVasquezVargas`
   * `GH_REPO`: `shopping-list-db`

## 📡 API Endpoints

### `GET /api/chat`
Checks the connection to the database and returns the current state of the shopping list.

**Success Response:**
```json
{
  "status": "core_online",
  "database_connected": "shopping-list-db",
  "current_list": { ... }
}
```

