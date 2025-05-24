from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ClientBase(BaseModel):
    name: str
    description: Optional[str] = None
    theme_settings: Optional[Dict[str, Any]] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(ClientBase):
    name: Optional[str] = None


class Client(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ModelBase(BaseModel):
    name: str
    client_id: int
    reference_image_path: Optional[str] = None


class ModelCreate(ModelBase):
    pass


class ModelUpdate(ModelBase):
    name: Optional[str] = None
    client_id: Optional[int] = None
    reference_image_path: Optional[str] = None


class Model(ModelBase):
    id: int
    base_embedding: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LayerBase(BaseModel):
    name: str
    type: str  # hair, outfit, scene
    prompt: str
    negative_prompt: Optional[str] = None
    strength: float = 1.0
    reference_image_path: Optional[str] = None


class LayerCreate(LayerBase):
    pass


class LayerUpdate(LayerBase):
    name: Optional[str] = None
    type: Optional[str] = None
    prompt: Optional[str] = None


class Layer(LayerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class ModelLayerBase(BaseModel):
    model_id: int
    layer_id: int
    settings: Optional[Dict[str, Any]] = None


class ModelLayerCreate(ModelLayerBase):
    pass


class ModelLayerUpdate(ModelLayerBase):
    model_id: Optional[int] = None
    layer_id: Optional[int] = None
    settings: Optional[Dict[str, Any]] = None


class ModelLayer(ModelLayerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class HistoryBase(BaseModel):
    model_id: int
    image_path: str
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class HistoryCreate(HistoryBase):
    pass


class History(HistoryBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True


class LookbookBase(BaseModel):
    client_id: int
    name: str
    description: Optional[str] = None


class LookbookCreate(LookbookBase):
    pass


class LookbookUpdate(LookbookBase):
    client_id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None


class Lookbook(LookbookBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class LookbookEntryBase(BaseModel):
    lookbook_id: int
    history_id: int
    order: int = 0
    notes: Optional[str] = None


class LookbookEntryCreate(LookbookEntryBase):
    pass


class LookbookEntryUpdate(LookbookEntryBase):
    lookbook_id: Optional[int] = None
    history_id: Optional[int] = None
    order: Optional[int] = None
    notes: Optional[str] = None


class LookbookEntry(LookbookEntryBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    username: str
    email: str
    role: str = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None


class GenerationRequest(BaseModel):
    model_id: int
    hair_layer_id: Optional[int] = None
    outfit_layer_id: Optional[int] = None
    scene_layer_id: Optional[int] = None
    prompt: Optional[str] = None
    negative_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class InpaintRequest(BaseModel):
    model_id: int
    image_path: str
    mask_path: str
    prompt: str
    negative_prompt: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None


class GenerationResponse(BaseModel):
    image_path: str
    history_id: int
