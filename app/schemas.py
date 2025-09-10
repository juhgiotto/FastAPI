from pydantic import BaseModel
from typing import Optional, List

class EstadosBase(BaseModel):
    sigla: str

class EstadosCreate(EstadosBase):
    pass

class Estado(EstadosBase):
    id:int
    class Config:
        orm_mode: True

class MunicipiosBase(BaseModel):
    nome: str
    numero_servidores: int
    estado_id: int

class MunicipiosCreate(MunicipiosBase):
    pass

class Municipio(MunicipiosBase):
    id:int
    class Config:
        orm_mode = True

class UsuariosBase(BaseModel):
    username: str
    perfil: str

class UsuarioCreate(UsuariosBase):
    senha: str

class Usuario(UsuariosBase):
    id: int
    class Config:
        orm_mode = True

class LoginData (BaseModel):
    username: str
    senha: str

class Token(BaseModel):
    access_token: str
    token_type: str