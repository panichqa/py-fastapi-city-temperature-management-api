from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app import models, schemas, crud, temperature


Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/cities", response_model=schemas.City)
def create_city(city: schemas.CityCreate, db: Session = Depends(get_db)):
    return crud.create_city(db=db, city=city)

@app.get("/cities", response_model=list[schemas.City])
def get_cities(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_cities(db=db, skip=skip, limit=limit)

@app.get("/cities/{city_id}", response_model=schemas.City)
def get_city(city_id: int, db: Session = Depends(get_db)):
    db_city = crud.get_city(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@app.put("/cities/{city_id}", response_model=schemas.City)
def update_city(city_id: int, city: schemas.CityCreate, db: Session = Depends(get_db)):
    db_city = crud.update_city(db=db, city_id=city_id, city=city)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@app.delete("/cities/{city_id}", response_model=schemas.City)
def delete_city(city_id: int, db: Session = Depends(get_db)):
    db_city = crud.delete_city(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(status_code=404, detail="City not found")
    return db_city

@app.post("/temperatures/update")
async def update_temperatures(db: Session = Depends(get_db)):
    await temperature.update_temperatures(db)
    return {"message": "Temperatures updated successfully"}

@app.get("/temperatures", response_model=list[schemas.Temperature])
def get_temperatures(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(models.Temperature).offset(skip).limit(limit).all()

@app.get("/temperatures/?city_id={city_id}", response_model=list[schemas.Temperature])
def get_temperatures_by_city(city_id: int, db: Session = Depends(get_db)):
    return db.query(models.Temperature).filter(models.Temperature.city_id == city_id).all()
