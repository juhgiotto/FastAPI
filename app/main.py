from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from . import models, database, auth
from fastapi.security import OAuth2PasswordRequestForm

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="API Servidores por municipio")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

"""@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.SessionLocal)):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Usuário ou senha invalidos")
    access_token = auth.create_access_token(data={"sub": user.username})
    return {"acess_token": access_token, "token_type": "bearer"}"""

@app.get("/")
def raiz():
    return {"mensagem": "API de servidores funcionando!"}

@app.get("/municipios")
def listar_municipios(db: Session = Depends(get_db)):
    return db.query(models.Municipio).all()

@app.get("/estados")
def listar_estados(db: Session = Depends(get_db)):
    return db.query(models.Estado).all()