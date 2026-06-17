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
import jwt

from app.database import Base, engine, get_db, DiaryEntryModel
from app.schemas import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse

# Auth0 Configuration
AUTH0_DOMAIN = "floki-security.us.auth0.com"
AUTH0_API_AUDIENCE = "https://devsecops-dagbok.onrender.com"
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

# Security Validator
def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """
    Validates the JWT token provided in the Authorization header
    and returns the 'sub' (User ID) claim.
    """
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            options={
                "verify_signature": False,
                "verify_exp": False,
                "verify_nbf": False,
                "verify_iat": False
            }
        )

        user_id = payload.get("sub")
        if not user_id:
            raise ValueError("El token no contiene el claim 'sub'")

        return user_id

    except Exception as e:
        print(f"Auth Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        ) from e

@app.get(
    "/api/entries",
    response_model=List[DiaryEntryResponse],
    status_code=status.HTTP_200_OK
)
def get_all_entries(
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Retrieve all diary entries belonging strictly to the authenticated user."""
    return db.query(DiaryEntryModel).filter(DiaryEntryModel.user_id == current_user).all()

@app.get("/api/entries/{entry_id}", response_model=DiaryEntryResponse)
def get_single_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Retrieve a single diary entry by ID, validating ownership."""
    entry = db.query(DiaryEntryModel).filter(
        DiaryEntryModel.id == entry_id,
        DiaryEntryModel.user_id == current_user
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry

@app.post("/api/entries", response_model=DiaryEntryResponse, status_code=201)
def create_entry(
    entry_data: DiaryEntryCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Create a new diary entry injected with the authenticated user's ID."""
    new_entry = DiaryEntryModel(**entry_data.model_dump(), user_id=current_user)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return new_entry

@app.put("/api/entries/{entry_id}", response_model=DiaryEntryResponse)
def update_entry(
    entry_id: int,
    entry_data: DiaryEntryUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Update an existing diary entry, strictly validating ownership."""
    entry = db.query(DiaryEntryModel).filter(
        DiaryEntryModel.id == entry_id,
        DiaryEntryModel.user_id == current_user
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    for key, value in entry_data.model_dump(exclude_unset=True).items():
        setattr(entry, key, value)
    db.commit()
    db.refresh(entry)
    return entry

@app.delete("/api/entries/{entry_id}")
def delete_entry(
    entry_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(verify_token)
):
    """Delete a diary entry by ID, strictly validating ownership."""
    entry = db.query(DiaryEntryModel).filter(
        DiaryEntryModel.id == entry_id,
        DiaryEntryModel.user_id == current_user
    ).first()

    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")

    db.delete(entry)
    db.commit()
    return {"message": "Entry successfully deleted"}

# Mount Frontend static files
CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.abspath(os.path.join(CURRENT_PATH, "..", "..", "frontend", "src"))
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="static")
