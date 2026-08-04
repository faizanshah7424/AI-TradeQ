# Installation Guide

## Prerequisites
- Node.js >= 20.x
- Python >= 3.11
- Docker & Docker Compose
- PostgreSQL 16 (or containerized via Docker)
- Redis 7 (or containerized via Docker)

## Local Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/codeorbit/ai-tradeq.git
   cd ai-tradeq
   ```
2. Setup Backend:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # Or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```
3. Setup Frontend:
   ```bash
   cd ../frontend
   npm install
   ```
