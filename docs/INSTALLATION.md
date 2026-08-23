# Installation Guide

## Prerequisites
- Python 3.12.x
- Node.js 22 LTS
- pnpm (or npm / corepack)
- PostgreSQL 16+
- Redis 7+
- Docker & Docker Compose

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
