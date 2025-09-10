from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base


# ---------- Estado ----------
class Estado(Base):
    __tablename__ = "estados"

    id = Column(Integer, primary_key=True, index=True)
    sigla = Column(String, unique=True, index=True)

    # Relacionamento 1:N -> um estado tem vários municípios
    municipios = relationship("Municipio", back_populates="estado")


# ---------- Municipio ----------
class Municipio(Base):
    __tablename__ = "municipios"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    numero_servidores = Column(Integer)

    estado_id = Column(Integer, ForeignKey("estados.id"))

    # Relacionamento N:1 -> um município pertence a um estado
    estado = relationship("Estado", back_populates="municipios")


# ---------- Usuario ----------
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    senha = Column(String)  # senha será armazenada com hash
    perfil = Column(String)  # admin ou leitor
