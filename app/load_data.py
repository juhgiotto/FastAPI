import csv
from app.database import SessionLocal, engine, Base
from app import models

Base.metadata.create_all(bind=engine)
db = SessionLocal()

with open("dados/servidores.csv", enconding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        sigla = row["sg_uf_municipio_uorg"]
        nome = row["no_municipio_uorg"]
        servidores =int(row["qtd_servidores_ativos"])
        estados = db.query(models.Estado).filter_by(sigla=sigla).first()
        if not estado:
            estado = models.Estado(sigla=sigla)
            db.add(estado)
            db.commit()
            db.refresh(estado)

        municipio= models.Municipio(
            nome=nome,
            numero_servidores=servidores,
            estado_id=estado.id
        )
        db.add(municipio)

db.commit()
db.close()