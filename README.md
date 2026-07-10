# Jod-AI

AI startup project

## Project Structure

```
jod-ai/
├── frontend/          # Next.js 15 with Tailwind CSS and shadcn/ui
│   ├── src/
│   │   ├── app/       # App router pages
│   │   └── components/# React components
│   └── public/        # Static assets
└── backend/           # FastAPI Python backend
    ├── main.py        # API entry point
    └── requirements.txt
```

## Getting Started

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at http://localhost:3000

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Backend runs at http://localhost:8000

## Development

- Frontend: Next.js 15 (App Router) + Tailwind CSS + shadcn/ui
- Backend: FastAPI + Uvicorn
