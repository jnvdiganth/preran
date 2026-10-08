# MotoCompare - Full Stack Motorcycle Comparison Platform

A full-stack application for exploring, filtering, comparing, and managing motorcycles. Built with a **FastAPI** backend and **SQLite** database, connected to a responsive dark-mode glassmorphic frontend.

---

## 🚀 Features

- **Full RESTful CRUD API**:
  - `GET /api/bikes`: Search by keyword, filter by brand, category, price range, and min CC, with sorting.
  - `GET /api/bikes/{id}`: Detailed specifications, pros, cons, and equipment.
  - `POST /api/bikes`: Add new motorcycles dynamically with JSON schema validation.
  - `PUT /api/bikes/{id}`: Update bike specs and details.
  - `DELETE /api/bikes/{id}`: Remove motorcycle from catalog.
- **Head-to-Head Comparison Engine (`/api/compare`)**:
  - Server-calculated specification advantages (power, torque, mileage, top speed, kerb weight, price).
  - Advantage counters and winner identification.
- **Dynamic Filter Discovery (`/api/filters`)**:
  - Automatically extracts available brands, types, and min/max bounds from the database.
- **User Favorites (`/api/favorites`)**:
  - Persistent favorite motorcycle bookmarks in SQLite.
- **Interactive API Documentation**:
  - Swagger UI available at `http://127.0.0.1:8000/docs`
  - ReDoc available at `http://127.0.0.1:8000/redoc`
- **Unified Serving**:
  - Frontend (`/static/index.html`) is served directly by FastAPI at `http://127.0.0.1:8000/`.

---

## 📁 Project Structure

```
c:\Users\Lenovo\bike.c\
├── main.py              # FastAPI application, routes, CORS & static file mounting
├── database.py          # SQLite database schema, connections, and initial bike seed data
├── schemas.py           # Pydantic validation and serialization models
├── requirements.txt     # Python package requirements
├── motocompare.db       # SQLite database (auto-generated on first run)
└── static/
    └── index.html       # Full frontend integrated with backend REST APIs
```

---

## ⚡ How to Run

1. Open PowerShell and navigate to the project directory:
   ```powershell
   cd C:\Users\Lenovo\bike.c
   ```

2. Start the FastAPI server using Uvicorn:
   ```powershell
   python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
   ```

3. Open your browser:
   - **Web Application**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive Swagger Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
