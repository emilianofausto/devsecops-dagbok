import os
from typing import List
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from app.database import Base, engine, get_db, DiaryEntryModel
from app.schemas import DiaryEntryCreate, DiaryEntryUpdate, DiaryEntryResponse

# Create database tables on application start
Base.metadata.create_all(bind=engine)

app = FastAPI(title="DevSecOps Diary API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/entries", response_model=List[DiaryEntryResponse], status_code=status.HTTP_200_OK)
def get_all_entries(db: Session = Depends(get_db)):
    return db.query(DiaryEntryModel).all()

@app.get("/api/entries/{entry_id}", response_model=DiaryEntryResponse, status_code=status.HTTP_200_OK)
def get_single_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Entry with ID {entry_id} not found"
        )
    return entry

@app.post("/api/entries", response_model=DiaryEntryResponse, status_code=status.HTTP_201_CREATED)
def create_entry(entry_data: DiaryEntryCreate, db: Session = Depends(get_db)):
    new_entry = DiaryEntryModel(**entry_data.model_dump())
    db.add(new_entry)
    db.commit()
    # db.refresh(new_entry)
    return new_entry

@app.put("/api/entries/{entry_id}", response_model=DiaryEntryResponse, status_code=status.HTTP_200_OK)
def update_entry(entry_id: int, entry_data: DiaryEntryUpdate, db: Session = Depends(get_db)):
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Entry with ID {entry_id} not found"
        )
    
    update_dict = entry_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Payload contains no valid modifications"
        )
        
    for key, value in update_dict.items():
        setattr(entry, key, value)
        
    db.commit()
    db.refresh(entry)
    return entry

@app.delete("/api/entries/{entry_id}", status_code=status.HTTP_200_OK)
def delete_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(DiaryEntryModel).filter(DiaryEntryModel.id == entry_id).first()
    if not entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f"Entry with ID {entry_id} not found"
        )
    db.delete(entry)
    db.commit()
    return {"message": f"Entry {entry_id} successfully deleted"}

current_dir = os.path.dirname(os.path.abspath(__file__))
frontend_dir = os.path.abspath(os.path.join(current_dir, "..", "..", "frontend"))
app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="static")
