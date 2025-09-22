from sqlalchemy.orm import Session
from models_db import engine, Servidor, Gratificacao

with Session(engine) as session:
    servidor = Servidor(
        nome="Júlia",
        cpf="12345678900",
        escolaridade="Superior",
        situacao="Ativo"
    )
    session.add(servidor)
    session.commit()

    grat = Gratificacao(
        nome_rubrica="RUB123",
        valor=500.00,
        servidor_id=servidor.id
    )
    session.add(grat)
    session.commit()

print("Dados inseridos com sucesso!")
