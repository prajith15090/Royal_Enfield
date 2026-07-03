# 🏍️ Royal Enfield API

A **FastAPI** REST API for managing Royal Enfield motorcycle data — bikes, variants, specs, and authorized dealers — backed by **Neon PostgreSQL**.

---

## 📁 Project Structure

```
RoyalEnfieldAPI/
├── app.py          # FastAPI app with all routes
├── database.py     # DB engine, session, and init_db()
├── models.py       # SQLAlchemy ORM models
├── requirements.txt
├── .env            # Environment variables (not committed)
└── README.md
```

---

## ⚙️ Setup

### 1. Clone & Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Your `.env` file should contain:

```env
DATABASE_URL=postgresql://neondb_owner:<password>@<host>/neondb?sslmode=require&channel_binding=require
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
SECRET_KEY=your-secret-key-here
```

### 3. Run the Server

```bash
python app.py
```

Or with uvicorn directly:

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

---

## 📖 API Endpoints

### 🔵 Health

| Method | Endpoint  | Description         |
|--------|-----------|---------------------|
| GET    | `/`       | Welcome message     |
| GET    | `/health` | DB connectivity check |

### 🏍️ Bikes

| Method | Endpoint         | Description                         |
|--------|------------------|-------------------------------------|
| GET    | `/bikes`         | List all bikes (filter by category) |
| GET    | `/bikes/{id}`    | Get a single bike                   |
| POST   | `/bikes`         | Add a new bike                      |
| PUT    | `/bikes/{id}`    | Update a bike                       |
| DELETE | `/bikes/{id}`    | Delete a bike                       |

### 🏪 Dealers

| Method | Endpoint           | Description                      |
|--------|--------------------|----------------------------------|
| GET    | `/dealers`         | List all dealers (filter by city)|
| GET    | `/dealers/{id}`    | Get a single dealer              |
| POST   | `/dealers`         | Add a new dealer                 |
| DELETE | `/dealers/{id}`    | Delete a dealer                  |

---

## 🧪 Interactive Docs

Once running, open:
- **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)

---

## 🗄️ Database

- Hosted on **Neon** (serverless PostgreSQL)
- Tables are auto-created on startup via `init_db()`
- Models: `Bike`, `Dealer`

---

## 📦 Tech Stack

| Layer      | Technology            |
|------------|-----------------------|
| Framework  | FastAPI               |
| ORM        | SQLAlchemy            |
| Database   | Neon PostgreSQL       |
| Validation | Pydantic v2           |
| Server     | Uvicorn               |
