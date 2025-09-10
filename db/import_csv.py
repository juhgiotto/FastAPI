import pandas as pd 
import re
from decimal import Decimal
from models_db import SessionLocal, Servidor, Cargo, Orgao, Unidade, Gratificacao
from sqlalchemy.exc import IntegrityError

CSV_PATH = "gratificacoes_202508.csv"

def get_or_create(session, model, defaults=None, **kwargs):
    instance = session.query(model).filter_by(**kwargs).one_or_none()
    if instance:
        return instance
    params = dict(**kwargs)
    if defaults:
        params.update(defaults)
    instance = model(**params)
    session.add(instance)
    try:
        session.flush()
    except IntegrityError:
        session.rollback()
        instance = session.query(model).filter_by(**kwargs).one()
    return instance

def safe_str(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s != "" else None

def normalize_cpf(cpf):
    if cpf is None:
        return None
    digits = re.sub(r"\D","", str(cpf))
    return digits if digits else None

def parse_valor(val):
    if pd.isna(val):
        return None
    s = str(val).strip()
    s = s.replace(",", ".")
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except Exception:
        return None
    
def main():
    print("Lendo CSV")
    df = pd.read_csv(CSV_PATH, encoding="utf-8", sep=";")
    print(f"{len(df)} linhas lidas.")

    session = SessionLocal()
    inserted = 0

    for idx, row in df.iterrows():
        #servidores
        cpf_raw = safe_str(row.get("CPF"))
        cpf = normalize_cpf(cpf_raw)
        if not cpf:
            cpf = f"NOCPF_{idx}"

        nome = safe_str(row.get("NOME_SERVIDOR")) or "SEM NOME"
        escolaridade_ser = safe_str(row.get("ESCOLARIDADE_SERVIDOR"))
        situacao = safe_str(row.get("SITUACAO_SERVIDOR"))

        servidor = session.query(Servidor).filter_by(cpf=cpf).one_or_none()
        if not servidor:
            servidor = Servidor(cpf=cpf, nome=nome, escolaridade = escolaridade_ser, situacao=situacao)
            session.add(servidor)
            session.flush()

        #Orgão
        org_ex_name = safe_str(row.get("ORGAO_EXERCICIO"))
        uf_uorg = safe_str(row.get("UF_UORG_EXERCICIO"))
        org_ex = None
        if org_ex_name:
            org_ex = get_or_create(session, Orgao, name=org_ex_name, uf=uf_uorg)

        uorg_ex_name = safe_str(row.get("UORG_EXERCICIO"))
        uorg_ex = None
        if uorg_ex_name:
            uorg_ex = get_or_create(session, Unidade, name=uorg_ex_name, uf=uf_uorg, orgao_id=org_ex.id if org_ex else None)

        upag_name = safe_str(row.get("UPAG"))
        uf_upag = safe_str(row.get("UF_UPAG"))
        upag = None
        if upag_name:
            upag = get_or_create(session, Unidade, name=upag_name, uf=uf_upag)

        #Cargos
        cargo = safe_str(row.get("CARGO"))
        pos =  None
        if cargo:
            pos = session.query(Cargo).filter_by(title=cargo).one_or_none()
            if not pos:
                pos = Cargo(title=cargo, escolaridade=safe_str(row.get("ESCOLARIDADE_CARGO")))
                session.add(pos)
                session.flush()

        cargo_origem_name = safe_str(row.get("CARGO_ORIGEM"))
        pos_origem = None
        if cargo_origem_name:
            pos_origem = session.query(Cargo).filter_by(title=cargo_origem_name, escolaridade=safe_str(row.get("ESCOLARIDADE_CARGO_ORIGEM")))
            session.add(pos_origem)
            session.flush()

        org_origem_name= safe_str(row.get("ORGAO_ORIGEM"))
        org_origem = None
        if org_origem_name:
            org_origem = get_or_create(session, Orgao, name=org_origem_name)

        #Gratificacões
        nome_rublica = safe_str(row.get("NOME_RUBRICA"))
        nivel = safe_str(row.get("NIVEL_GRATIFICACAO"))
        valor = parse_valor(row.get("VALOR"))

        grat = Gratificacao(
            servidor_id = servidor.id,
            cargo_id = pos.id if pos else None,
            org_exercicio_id = org_ex.id if org_ex else None,
            uorg_exercicio_id = uorg_ex.id if uorg_ex else None,
            upag_id = upag.id if upag else None,
            org_origem_id = org_origem.id if org_origem else None,
            nome_rubrica = nome_rublica,
            nivel_gratificacao = nivel,
            valor = valor
        )
        session.add(grat)
        inserted += 1

        #Limite de inserções por memória
        if inserted % 500 == 0:
            session.commit()
            print(f"Commited {inserted} registros")

    session.commit()
    print(f"Importação finalizada. {inserted} gratificações inseridas.")
    session.close()

    if __name__ == "__main__":
        main()
