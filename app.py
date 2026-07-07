from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import os

from database import get_db, init_db, run_migrations
from models import Bike, Dealer, Booking, ChatHistory

load_dotenv()

# ─────────────────────────────────────────────
# App Initialization
# ─────────────────────────────────────────────
app = FastAPI(
    title="Royal Enfield API",
    description="REST API for Royal Enfield motorcycles, variants, and dealer information.",
    version="1.0.0",
    contact={"name": "Royal Enfield Dev Team"},
    docs_url="/docs",
    redoc_url="/redoc",
)


@app.on_event("startup")
def on_startup():
    """Initialize database tables and run migrations on startup."""
    init_db()
    run_migrations()


# ─────────────────────────────────────────────
# Pydantic Schemas
# ─────────────────────────────────────────────
class BikeCreate(BaseModel):
    name: str
    model_code: str
    category: str
    variant: Optional[str] = None
    color: Optional[str] = None
    price_inr: float
    engine_cc: Optional[int] = None
    engine_type: Optional[str] = None
    max_power_bhp: Optional[float] = None
    max_torque_nm: Optional[float] = None
    transmission: Optional[str] = None
    weight_kg: Optional[float] = None
    fuel_tank_litres: Optional[float] = None
    seat_height_mm: Optional[int] = None
    is_available: Optional[bool] = True
    year_launched: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class BikeResponse(BikeCreate):
    id: int

    class Config:
        from_attributes = True


class DealerCreate(BaseModel):
    name: str
    city: str
    state: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: Optional[bool] = True


class DealerResponse(DealerCreate):
    id: int

    class Config:
        from_attributes = True


# ─────────────────────────────────────────────
# Booking Schemas
# ─────────────────────────────────────────────
class BookingPayload(BaseModel):
    """
    Accepts any combination of fields from any Kissflow phase.
    Only booking_id is required — all other fields are optional.
    Matches the actual Neon DB bookings table schema exactly.
    """
    # Identity
    booking_id:       str
    request_id:       Optional[str]   = None   # Kissflow request ID

    # Phase 1 – Initial Booking
    customer_name:    Optional[str]   = None
    email:            Optional[str]   = None
    city:             Optional[str]   = None
    interested_model: Optional[str]   = None
    variant:          Optional[str]   = None
    on_road_price:    Optional[float] = None
    booking_amount:   Optional[float] = None
    finance_required: Optional[str]   = None

    # Phase 2 – Finance
    preferred_bank:   Optional[str]   = None
    down_payment:     Optional[float] = None
    loan_amount:      Optional[float] = None
    loan_tenure:      Optional[str]   = None
    loan_status:      Optional[str]   = None

    # Phase 3 – Vehicle Allocation
    vehicle_available: Optional[str]  = None
    chassis_number:    Optional[str]  = None
    engine_number:     Optional[str]  = None

    # Phase 4 – Delivery
    delivery_status:     Optional[str] = None
    registration_status: Optional[str] = None
    insurance_status:    Optional[str] = None

    # Workflow
    workflow_stage:      Optional[str] = None


class BookingResponse(BaseModel):
    booking_id:          str
    request_id:          Optional[str]   = None
    customer_name:       Optional[str]   = None
    email:               Optional[str]   = None
    city:                Optional[str]   = None
    interested_model:    Optional[str]   = None
    variant:             Optional[str]   = None
    on_road_price:       Optional[float] = None
    booking_amount:      Optional[float] = None
    finance_required:    Optional[str]   = None
    preferred_bank:      Optional[str]   = None
    down_payment:        Optional[float] = None
    loan_amount:         Optional[float] = None
    loan_tenure:         Optional[str]   = None
    loan_status:         Optional[str]   = None
    vehicle_available:   Optional[str]   = None
    chassis_number:      Optional[str]   = None
    engine_number:       Optional[str]   = None
    delivery_status:     Optional[str]   = None
    registration_status: Optional[str]   = None
    insurance_status:    Optional[str]   = None
    workflow_stage:      Optional[str]   = None

    class Config:
        from_attributes = True



# ─────────────────────────────────────────────
# Root & Health
# ─────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"message": "Welcome to Royal Enfield API 🏍️", "status": "running", "docs": "/docs"}


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(__import__("sqlalchemy").text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unreachable: {str(e)}")


# ─────────────────────────────────────────────
# Bikes Endpoints
# ─────────────────────────────────────────────
@app.get("/bikes", response_model=List[BikeResponse], tags=["Bikes"])
def get_all_bikes(
    category: Optional[str] = None,
    available: Optional[bool] = None,
    db: Session = Depends(get_db),
):
    """Retrieve all bikes, optionally filtered by category or availability."""
    query = db.query(Bike)
    if category:
        query = query.filter(Bike.category.ilike(f"%{category}%"))
    if available is not None:
        query = query.filter(Bike.is_available == available)
    return query.all()


@app.get("/bikes/{bike_id}", response_model=BikeResponse, tags=["Bikes"])
def get_bike(bike_id: int, db: Session = Depends(get_db)):
    """Retrieve a single bike by ID."""
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    return bike


@app.post("/bikes", response_model=BikeResponse, status_code=status.HTTP_201_CREATED, tags=["Bikes"])
def create_bike(bike_data: BikeCreate, db: Session = Depends(get_db)):
    """Add a new Royal Enfield motorcycle."""
    existing = db.query(Bike).filter(Bike.model_code == bike_data.model_code).first()
    if existing:
        raise HTTPException(status_code=400, detail="Bike with this model_code already exists")
    bike = Bike(**bike_data.model_dump())
    db.add(bike)
    db.commit()
    db.refresh(bike)
    return bike


@app.put("/bikes/{bike_id}", response_model=BikeResponse, tags=["Bikes"])
def update_bike(bike_id: int, bike_data: BikeCreate, db: Session = Depends(get_db)):
    """Update an existing bike record."""
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    for key, value in bike_data.model_dump().items():
        setattr(bike, key, value)
    db.commit()
    db.refresh(bike)
    return bike


@app.delete("/bikes/{bike_id}", tags=["Bikes"])
def delete_bike(bike_id: int, db: Session = Depends(get_db)):
    """Delete a bike by ID."""
    bike = db.query(Bike).filter(Bike.id == bike_id).first()
    if not bike:
        raise HTTPException(status_code=404, detail="Bike not found")
    db.delete(bike)
    db.commit()
    return {"message": f"Bike {bike_id} deleted successfully"}


# ─────────────────────────────────────────────
# Booking Endpoint  (Kissflow → API → Neon DB)
# ─────────────────────────────────────────────
@app.post("/booking", response_model=BookingResponse, tags=["Bookings"])
def save_booking(payload: BookingPayload, db: Session = Depends(get_db)):
    """
    **Smart Upsert** — handles every Kissflow workflow phase.

    - **First call** (booking_id not in DB) → INSERT a new row with
      whatever fields are provided; everything else stays NULL.
    - **Subsequent calls** (booking_id exists) → UPDATE *only* the
      fields present in this payload; existing data is never overwritten
      with NULL.
    """
    try:
        # Extract only the fields that were actually sent (exclude booking_id itself)
        incoming = payload.model_dump(exclude_unset=True)
        incoming.pop("booking_id", None)

        existing = db.query(Booking).filter(
            Booking.booking_id == payload.booking_id
        ).first()

        if existing is None:
            # ── INSERT ──────────────────────────────────────────────────
            new_booking = Booking(
                booking_id=payload.booking_id,
                **incoming
            )
            db.add(new_booking)
            db.commit()
            db.refresh(new_booking)
            return new_booking
        else:
            # ── PATCH (only non-null incoming fields) ────────────────────
            for field, value in incoming.items():
                if value is not None:          # never overwrite existing data with NULL
                    setattr(existing, field, value)
            db.commit()
            db.refresh(existing)
            return existing

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "type": type(e).__name__,
                "received_payload": payload.model_dump(exclude_unset=True)
            }
        )


@app.get("/booking", response_model=List[BookingResponse], tags=["Bookings"])
def get_all_bookings(db: Session = Depends(get_db)):
    """List every booking with its current lifecycle state."""
    return db.query(Booking).all()


@app.get("/booking/debug", tags=["Bookings"])
def debug_booking_table(db: Session = Depends(get_db)):
    """
    Debug endpoint — returns actual columns in the bookings table.
    Must be defined BEFORE /booking/{booking_id} to avoid route shadowing.
    """
    from sqlalchemy import inspect
    try:
        inspector = inspect(db.bind)
        columns = inspector.get_columns("bookings")
        return {
            "table_exists": True,
            "columns": [c["name"] for c in columns],
            "expected_columns": [
                "booking_id", "customer_name", "email", "city",
                "interested_model", "finance_required",
                "preferred_bank", "loan_amount", "loan_status",
                "vehicle_available", "chassis_number", "engine_number",
                "delivery_status", "registration_status", "insurance_status",
                "created_at", "updated_at"
            ]
        }
    except Exception as e:
        return {"table_exists": False, "error": str(e)}


@app.get("/booking/{booking_id}", response_model=BookingResponse, tags=["Bookings"])
def get_booking(booking_id: str, db: Session = Depends(get_db)):
    """Retrieve a single booking by its ID."""
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail=f"Booking '{booking_id}' not found")
    return booking


# ─────────────────────────────────────────────
# Dealers Endpoints
# ─────────────────────────────────────────────
@app.get("/dealers", response_model=List[DealerResponse], tags=["Dealers"])
def get_all_dealers(city: Optional[str] = None, db: Session = Depends(get_db)):
    query = db.query(Dealer)
    if city:
        query = query.filter(Dealer.city.ilike(f"%{city}%"))
    return query.all()


@app.get("/dealers/{dealer_id}", response_model=DealerResponse, tags=["Dealers"])
def get_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    return dealer


@app.post("/dealers", response_model=DealerResponse, status_code=status.HTTP_201_CREATED, tags=["Dealers"])
def create_dealer(dealer_data: DealerCreate, db: Session = Depends(get_db)):
    dealer = Dealer(**dealer_data.model_dump())
    db.add(dealer)
    db.commit()
    db.refresh(dealer)
    return dealer


@app.delete("/dealers/{dealer_id}", tags=["Dealers"])
def delete_dealer(dealer_id: int, db: Session = Depends(get_db)):
    dealer = db.query(Dealer).filter(Dealer.id == dealer_id).first()
    if not dealer:
        raise HTTPException(status_code=404, detail="Dealer not found")
    db.delete(dealer)
    db.commit()
    return {"message": f"Dealer {dealer_id} deleted successfully"}


# ─────────────────────────────────────────────
# AI Assistant Endpoint (Kissflow Chatbot)
# ─────────────────────────────────────────────
class ChatPayload(BaseModel):
    question: str

class ChatResponse(BaseModel):
    reply: str

from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.post("/chat", response_model=ChatResponse, tags=["AI Assistant"])
def chat_endpoint(payload: ChatPayload, db: Session = Depends(get_db)):
    """
    Receives a question from the Kissflow AI Assistant popup,
    returns an answer using OpenAI, and logs the interaction to Neon DB.
    """
    try:
        # Ask OpenAI for the answer
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful and polite Royal Enfield customer support assistant. Answer questions clearly and concisely about motorcycles, prices, and test rides."},
                {"role": "user", "content": payload.question}
            ],
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message.content
    except Exception as e:
        reply = "I'm having trouble connecting to my AI brain right now. Please try again later!"
        print(f"OpenAI Error: {e}")
        
    # Save the chat to Neon DB
    chat_log = ChatHistory(question=payload.question, reply=reply)
    db.add(chat_log)
    db.commit()
        
    return {"reply": reply}

from fastapi.responses import HTMLResponse

@app.get("/bot", response_class=HTMLResponse, tags=["AI Assistant"])
def chat_ui():
    """
    Serves a beautiful, standalone HTML Chatbot interface.
    This can be embedded inside Kissflow using an iFrame/URL component.
    """
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Royal Enfield AI Assistant</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #121212;
                color: #ffffff;
                margin: 0;
                padding: 0;
                display: flex;
                flex-direction: column;
                height: 100vh;
            }
            .header {
                background-color: #d62828;
                padding: 15px;
                text-align: center;
                font-weight: bold;
                font-size: 18px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.5);
            }
            .chat-container {
                flex-grow: 1;
                padding: 20px;
                overflow-y: auto;
                display: flex;
                flex-direction: column;
                gap: 15px;
            }
            .message {
                max-width: 80%;
                padding: 12px 16px;
                border-radius: 20px;
                line-height: 1.4;
                font-size: 15px;
            }
            .user-msg {
                align-self: flex-end;
                background-color: #2b2b2b;
                border-bottom-right-radius: 2px;
            }
            .bot-msg {
                align-self: flex-start;
                background-color: #d62828;
                border-bottom-left-radius: 2px;
            }
            .input-area {
                padding: 15px;
                background-color: #1e1e1e;
                display: flex;
                gap: 10px;
                border-top: 1px solid #333;
            }
            input[type="text"] {
                flex-grow: 1;
                padding: 12px;
                border-radius: 25px;
                border: 1px solid #444;
                background-color: #2b2b2b;
                color: white;
                outline: none;
                font-size: 15px;
            }
            input[type="text"]:focus {
                border-color: #d62828;
            }
            button {
                background-color: #d62828;
                color: white;
                border: none;
                border-radius: 25px;
                padding: 0 20px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.2s;
            }
            button:hover {
                background-color: #b52222;
            }
            .loading {
                font-style: italic;
                color: #aaa;
                font-size: 13px;
                align-self: flex-start;
                display: none;
            }
        </style>
    </head>
    <body>
        <div class="header">
            Royal Enfield AI Assistant
        </div>
        <div class="chat-container" id="chat-container">
            <div class="message bot-msg">Hello! I am your Royal Enfield AI Assistant. How can I help you today?</div>
        </div>
        <div class="loading" id="loading">Thinking...</div>
        <div class="input-area">
            <input type="text" id="question" placeholder="Ask about bikes, prices, test rides..." onkeypress="handleKeyPress(event)">
            <button onclick="sendMessage()">Send</button>
        </div>

        <script>
            async function sendMessage() {
                const input = document.getElementById('question');
                const chatContainer = document.getElementById('chat-container');
                const loading = document.getElementById('loading');
                const question = input.value.trim();

                if (!question) return;

                // Add user message to UI
                const userDiv = document.createElement('div');
                userDiv.className = 'message user-msg';
                userDiv.textContent = question;
                chatContainer.appendChild(userDiv);

                input.value = '';
                loading.style.display = 'block';
                chatContainer.scrollTop = chatContainer.scrollHeight;

                try {
                    // Send to backend
                    const response = await fetch('/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ question: question })
                    });
                    
                    const data = await response.json();

                    // Add bot message to UI
                    const botDiv = document.createElement('div');
                    botDiv.className = 'message bot-msg';
                    botDiv.textContent = data.reply;
                    chatContainer.appendChild(botDiv);

                } catch (error) {
                    const errorDiv = document.createElement('div');
                    errorDiv.className = 'message bot-msg';
                    errorDiv.textContent = "Sorry, I couldn't reach my brain. Please try again.";
                    chatContainer.appendChild(errorDiv);
                } finally {
                    loading.style.display = 'none';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }

            function handleKeyPress(event) {
                if (event.key === 'Enter') {
                    sendMessage();
                }
            }
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", 8000)),
        reload=bool(os.getenv("DEBUG", True)),
    )
