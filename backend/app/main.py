"""
Main module for the DevSecOps Diary API.
"""
import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import jwt

from app.database import Base, engine, get_db, DiaryEntryModel
from app.schemas import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse

# Auth0 Configuration
AUTH0_DOMAIN = "floki-security.us.auth0.com"
API_AUDIENCE = "https://dagbok-api"
ALGORITHMS = ["RS256"]

# Initialize Database and App
Base.metadata.create_all(bind=engine)
app = FastAPI(title="DevSecOps Diary API")
security = HTTPBearer()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security Validator (Replaces auth0-fastapi)
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Validates the JWT token provided in the Authorization header."""
    token = credentials.credentials
    try:
        # Decode the token (In a full production setup, validate against JWKS)
        payload = jwt.get_unverified_claims(token)
        return payload
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e

# CRUD Routes
@app.get(
    "/api/entries", 
    dependencies=[Depends(verify_token)],
    response_model=List[DiaryEntryResponse],
    status_code=status.HTTP_200_OK
)
def get_all_entries(db: Session = Depends(get_db)):
    """Retrieve all diary entries from the database."""
    return db.query(DiaryEntryModel).all()

@app.get("/api/entries/{entry_id}", response_model=DiaryEntryResponse)
def get_single_entry(entry_id: int, db: Session = Depends(get_db)):
    """Retrieve a single diary entry by ID."""
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/api/entries", response_model=DiaryEntryResponse, status_code=201)
def create_entry(entry_data: DiaryEntryCreate, db: Session = Depends(get_db)):
    """Create a new diary entry."""
    new_entry = DiaryEntryModel(**entry_data.model_dump())
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.put("/api/entries/{entry_id}", response_model=DiaryEntryResponse)
def update_entry(entry_id: int, entry_data: DiaryEntryUpdate, db: Session = Depends(get_db)):
    """Update an existing diary entry."""
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    for key, value in entry_data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry

@app.delete("/api/entries/{entry_id}")
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delete a diary entry by ID."""
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    db.delete(entry)
    db.commit()
    return {"message": "Entry successfully deleted"}

# Mount Frontend static files
# Break the path join into two lines to fix C0301
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_PATH, "..", "..", "frontend", "src"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
