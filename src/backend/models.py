from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    theme_settings = Column(JSON, nullable=True)

    # Relationships
    models = relationship("Model", back_populates="client", cascade="all, delete-orphan")
    lookbooks = relationship("Lookbook", back_populates="client", cascade="all, delete-orphan")


class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String, index=True)
    base_embedding = Column(String)  # Path to the stored embedding file
    reference_image_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="models")
    model_layers = relationship("ModelLayer", back_populates="model", cascade="all, delete-orphan")
    histories = relationship("History", back_populates="model", cascade="all, delete-orphan")


class Layer(Base):
    __tablename__ = "layers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    type = Column(String, index=True)  # hair, outfit, scene
    prompt = Column(Text)
    negative_prompt = Column(Text, nullable=True)
    strength = Column(Float, default=1.0)
    reference_image_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    model_layers = relationship("ModelLayer", back_populates="layer")


class ModelLayer(Base):
    __tablename__ = "model_layers"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    layer_id = Column(Integer, ForeignKey("layers.id"))
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    model = relationship("Model", back_populates="model_layers")
    layer = relationship("Layer", back_populates="model_layers")


class History(Base):
    __tablename__ = "histories"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"))
    image_path = Column(String)
    prompt = Column(Text, nullable=True)
    negative_prompt = Column(Text, nullable=True)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    model = relationship("Model", back_populates="histories")
    lookbook_entries = relationship("LookbookEntry", back_populates="history", cascade="all, delete-orphan")


class Lookbook(Base):
    __tablename__ = "lookbooks"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    client = relationship("Client", back_populates="lookbooks")
    lookbook_entries = relationship("LookbookEntry", back_populates="lookbook", cascade="all, delete-orphan")


class LookbookEntry(Base):
    __tablename__ = "lookbook_entries"

    id = Column(Integer, primary_key=True, index=True)
    lookbook_id = Column(Integer, ForeignKey("lookbooks.id"))
    history_id = Column(Integer, ForeignKey("histories.id"))
    order = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    lookbook = relationship("Lookbook", back_populates="lookbook_entries")
    history = relationship("History", back_populates="lookbook_entries")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Integer, default=1)
    role = Column(String, default="user")  # admin, user
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
