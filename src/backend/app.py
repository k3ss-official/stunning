from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import os
import shutil
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from PIL import Image
import logging

from . import models, schemas
from .database import SessionLocal, engine, get_db
from .ai_models.stable_diffusion import StableDiffusionModel

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Stunning Modeling Studio API",
    description="API for the Stunning Modeling Studio system",
    version="1.0.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY", "development_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Initialize AI model
sd_model = StableDiffusionModel()

# Create required directories
os.makedirs("uploads", exist_ok=True)
os.makedirs("generated", exist_ok=True)

# Security functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def authenticate_user(db: Session, username: str, password: str):
    user = db.query(models.User).filter(models.User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: schemas.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

# Authentication endpoints
@app.post("/token", response_model=schemas.Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

# User endpoints
@app.post("/users/", response_model=schemas.User)
async def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    # Only admins can create users
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to create users")
    
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/users/me/", response_model=schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

# Client endpoints
@app.post("/clients/", response_model=schemas.Client)
async def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_client = models.Client(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client

@app.get("/clients/", response_model=List[schemas.Client])
async def read_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    clients = db.query(models.Client).offset(skip).limit(limit).all()
    return clients

@app.get("/clients/{client_id}", response_model=schemas.Client)
async def read_client(client_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    return db_client

@app.put("/clients/{client_id}", response_model=schemas.Client)
async def update_client(client_id: int, client: schemas.ClientUpdate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    update_data = client.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client

@app.delete("/clients/{client_id}", response_model=schemas.Client)
async def delete_client(client_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    db.delete(db_client)
    db.commit()
    return db_client

# Model endpoints
@app.post("/models/", response_model=schemas.Model)
async def create_model(
    client_id: int = Form(...),
    name: str = Form(...),
    reference_images: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Check if client exists
    db_client = db.query(models.Client).filter(models.Client.id == client_id).first()
    if db_client is None:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Save reference images
    reference_image_paths = []
    for i, file in enumerate(reference_images):
        file_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}_{file.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        reference_image_paths.append(file_path)
    
    # Use the first image as the main reference
    main_reference_path = reference_image_paths[0] if reference_image_paths else None
    
    # Create base embedding using Stable Diffusion
    embedding_path = sd_model.create_embedding(reference_image_paths)
    
    # Create model in database
    db_model = models.Model(
        client_id=client_id,
        name=name,
        base_embedding=embedding_path,
        reference_image_path=main_reference_path
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    
    return db_model

@app.get("/models/", response_model=List[schemas.Model])
async def read_models(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    query = db.query(models.Model)
    if client_id is not None:
        query = query.filter(models.Model.client_id == client_id)
    
    models_list = query.offset(skip).limit(limit).all()
    return models_list

@app.get("/models/{model_id}", response_model=schemas.Model)
async def read_model(model_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    return db_model

@app.delete("/models/{model_id}", response_model=schemas.Model)
async def delete_model(model_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(db_model)
    db.commit()
    return db_model

# Layer endpoints
@app.post("/layers/", response_model=schemas.Layer)
async def create_layer(
    name: str = Form(...),
    type: str = Form(...),
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(None),
    strength: float = Form(1.0),
    reference_image: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Save reference image if provided
    reference_image_path = None
    if reference_image:
        file_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_{reference_image.filename}"
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(reference_image.file, buffer)
        reference_image_path = file_path
    
    # Create layer in database
    db_layer = models.Layer(
        name=name,
        type=type,
        prompt=prompt,
        negative_prompt=negative_prompt,
        strength=strength,
        reference_image_path=reference_image_path
    )
    db.add(db_layer)
    db.commit()
    db.refresh(db_layer)
    
    return db_layer

@app.get("/layers/", response_model=List[schemas.Layer])
async def read_layers(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    query = db.query(models.Layer)
    if type is not None:
        query = query.filter(models.Layer.type == type)
    
    layers = query.offset(skip).limit(limit).all()
    return layers

@app.get("/layers/{layer_id}", response_model=schemas.Layer)
async def read_layer(layer_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_layer = db.query(models.Layer).filter(models.Layer.id == layer_id).first()
    if db_layer is None:
        raise HTTPException(status_code=404, detail="Layer not found")
    return db_layer

@app.delete("/layers/{layer_id}", response_model=schemas.Layer)
async def delete_layer(layer_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_layer = db.query(models.Layer).filter(models.Layer.id == layer_id).first()
    if db_layer is None:
        raise HTTPException(status_code=404, detail="Layer not found")
    
    db.delete(db_layer)
    db.commit()
    return db_layer

# Generation endpoints
@app.post("/generate/", response_model=schemas.GenerationResponse)
async def generate_image(
    request: schemas.GenerationRequest,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Get model
    db_model = db.query(models.Model).filter(models.Model.id == request.model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Get layers
    hair_layer = None
    outfit_layer = None
    scene_layer = None
    
    if request.hair_layer_id:
        db_hair = db.query(models.Layer).filter(models.Layer.id == request.hair_layer_id).first()
        if db_hair:
            hair_layer = {
                "prompt": db_hair.prompt,
                "negative_prompt": db_hair.negative_prompt,
                "strength": db_hair.strength,
                "reference_image_path": db_hair.reference_image_path
            }
    
    if request.outfit_layer_id:
        db_outfit = db.query(models.Layer).filter(models.Layer.id == request.outfit_layer_id).first()
        if db_outfit:
            outfit_layer = {
                "prompt": db_outfit.prompt,
                "negative_prompt": db_outfit.negative_prompt,
                "strength": db_outfit.strength,
                "reference_image_path": db_outfit.reference_image_path
            }
    
    if request.scene_layer_id:
        db_scene = db.query(models.Layer).filter(models.Layer.id == request.scene_layer_id).first()
        if db_scene:
            scene_layer = {
                "prompt": db_scene.prompt,
                "negative_prompt": db_scene.negative_prompt,
                "strength": db_scene.strength,
                "reference_image_path": db_scene.reference_image_path
            }
    
    # Generate image
    output_path = f"generated/{datetime.now().strftime('%Y%m%d%H%M%S')}.png"
    _, image_path = sd_model.apply_styling_layers(
        base_model_path=db_model.base_embedding,
        hair_layer=hair_layer,
        outfit_layer=outfit_layer,
        scene_layer=scene_layer,
        prompt=request.prompt or "",
        negative_prompt=request.negative_prompt or "",
        output_path=output_path,
        **(request.settings or {})
    )
    
    # Save to history
    db_history = models.History(
        model_id=request.model_id,
        image_path=image_path,
        prompt=request.prompt,
        negative_prompt=request.negative_prompt,
        settings=request.settings
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return {"image_path": image_path, "history_id": db_history.id}

@app.post("/inpaint/", response_model=schemas.GenerationResponse)
async def inpaint_image(
    model_id: int = Form(...),
    prompt: str = Form(...),
    negative_prompt: Optional[str] = Form(None),
    image: UploadFile = File(...),
    mask: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Get model
    db_model = db.query(models.Model).filter(models.Model.id == model_id).first()
    if db_model is None:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # Save uploaded images
    image_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_image.png"
    with open(image_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
    
    mask_path = f"uploads/{datetime.now().strftime('%Y%m%d%H%M%S')}_mask.png"
    with open(mask_path, "wb") as buffer:
        shutil.copyfileobj(mask.file, buffer)
    
    # Load images
    img = Image.open(image_path)
    mask_img = Image.open(mask_path)
    
    # Perform inpainting
    output_path = f"generated/{datetime.now().strftime('%Y%m%d%H%M%S')}_inpainted.png"
    _, result_path = sd_model.inpaint_image(
        image=img,
        mask_image=mask_img,
        prompt=prompt,
        negative_prompt=negative_prompt,
        output_path=output_path
    )
    
    # Save to history
    db_history = models.History(
        model_id=model_id,
        image_path=result_path,
        prompt=prompt,
        negative_prompt=negative_prompt,
        settings={"inpaint": True}
    )
    db.add(db_history)
    db.commit()
    db.refresh(db_history)
    
    return {"image_path": result_path, "history_id": db_history.id}

# History endpoints
@app.get("/histories/", response_model=List[schemas.History])
async def read_histories(
    skip: int = 0,
    limit: int = 100,
    model_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    query = db.query(models.History)
    if model_id is not None:
        query = query.filter(models.History.model_id == model_id)
    
    histories = query.order_by(models.History.created_at.desc()).offset(skip).limit(limit).all()
    return histories

@app.get("/histories/{history_id}", response_model=schemas.History)
async def read_history(history_id: int, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_history = db.query(models.History).filter(models.History.id == history_id).first()
    if db_history is None:
        raise HTTPException(status_code=404, detail="History not found")
    return db_history

# Lookbook endpoints
@app.post("/lookbooks/", response_model=schemas.Lookbook)
async def create_lookbook(lookbook: schemas.LookbookCreate, db: Session = Depends(get_db), current_user: schemas.User = Depends(get_current_active_user)):
    db_lookbook = models.Lookbook(**lookbook.dict())
    db.add(db_lookbook)
    db.commit()
    db.refresh(db_lookbook)
    return db_lookbook

@app.get("/lookbooks/", response_model=List[schemas.Lookbook])
async def read_lookbooks(
    skip: int = 0,
    limit: int = 100,
    client_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    query = db.query(models.Lookbook)
    if client_id is not None:
        query = query.filter(models.Lookbook.client_id == client_id)
    
    lookbooks = query.offset(skip).limit(limit).all()
    return lookbooks

@app.post("/lookbooks/{lookbook_id}/entries/", response_model=schemas.LookbookEntry)
async def add_lookbook_entry(
    lookbook_id: int,
    entry: schemas.LookbookEntryCreate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Check if lookbook exists
    db_lookbook = db.query(models.Lookbook).filter(models.Lookbook.id == lookbook_id).first()
    if db_lookbook is None:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    
    # Check if history exists
    db_history = db.query(models.History).filter(models.History.id == entry.history_id).first()
    if db_history is None:
        raise HTTPException(status_code=404, detail="History not found")
    
    # Create entry
    db_entry = models.LookbookEntry(**entry.dict())
    db.add(db_entry)
    db.commit()
    db.refresh(db_entry)
    
    return db_entry

@app.get("/lookbooks/{lookbook_id}/entries/", response_model=List[schemas.LookbookEntry])
async def read_lookbook_entries(
    lookbook_id: int,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_active_user)
):
    # Check if lookbook exists
    db_lookbook = db.query(models.Lookbook).filter(models.Lookbook.id == lookbook_id).first()
    if db_lookbook is None:
        raise HTTPException(status_code=404, detail="Lookbook not found")
    
    entries = db.query(models.LookbookEntry).filter(
        models.LookbookEntry.lookbook_id == lookbook_id
    ).order_by(models.LookbookEntry.order).offset(skip).limit(limit).all()
    
    return entries

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
