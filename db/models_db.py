from sqlalchemy import (create_engine, Column, Integer, String, Numeric, ForeignKey, UniqueConstraint)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./gratificacoes.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

Base = declarative_base()

class Orgao(Base):
    __tablename__ = "orgaos"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    uf = Column(String(2))

    unidades = relationship("Unidade", back_populates="orgao")

class Unidade(Base):
    __tablename__ = "unidades"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    uf = Column(String(2))
    orgao_id = Column(Integer, ForeignKey("orgaos.id"), nullable=True)
    orgao = relationship("Orgao", back_populates="unidades")

    __table_args__ = (UniqueConstraint("name", "orgao_id", name="uq_unit_name_org"),)

class Cargo(Base):
    __tablename__ = "cargos"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False, unique=True)
    escolaridade = Column(String, nullable=True)

class Servidor(Base):
    __tablename__ = "servidores"
    id = Column(Integer,primary_key=True)
    cpf = Column(String, nullable=False,  unique=True, index=True)
    name= Column(String, nullable=False)
    escolaridade = Column(String)
    situacao = Column(String)

    gratificacoes = relationship("Gratificacao", back_populates="employee")

class Gratificacao(Base):
    __tablename__ = "gratificacoes"
    id = Column(Integer, primary_key=True)

    servidor_id = Column(Integer, ForeignKey("servidores.id"),nullable=False)
    cargo_id = Column(Integer, ForeignKey("cargos.id"),nullable=True)

    org_exercicio_id = Column(Integer, ForeignKey("orgaos.id"), nullable=True)
    uorg_exercicio_id = Column(Integer, ForeignKey("unidades.id"),nullable=True)
    upag_id = Column(Integer, ForeignKey("unidades.id"), nullable=True)
    org_origem_id = Column(Integer, ForeignKey("orgaos.id"), nullable=True)
    cargo_origem_id = Column(Integer, ForeignKey("cargos.id"), nullable=True)

    nome_rubrica = Column(String)
    nivel_gratificacao = Column(String)
    valor = Column(Numeric(14,2))

    servidor = relationship("Servidor", back_populates="gratificacoes")
    cargo = relationship("Cargo", foreign_keys=[cargo_id])
    cargo_origem = relationship("Cargo", foreign_keys=[cargo_origem_id])
    org_exercicio = relationship("Orgao",  foreign_keys=[org_exercicio_id])
    org_origem = relationship("Orgao", foreign_keys=[org_origem_id])
    uorg_exercicio = relationship("Unidade", foreign_keys=[uorg_exercicio_id])
    upag = relationship("Unidade", foreign_keys=[upag_id])