import pandas as pd
import re
from decimal import Decimal
from models_db import SessionLocal, Servidor, Cargo, Orgao, Unidade, Gratificacao

CSV_PATH = "gratificacoes_202508.csv"

def safe_str(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s != "" else None

def normalize_cpf(cpf):
    """Remove caracteres não numéricos e completa zeros à esquerda até 11 dígitos"""
    if cpf is None:
        return None
    digits = re.sub(r"\D", "", str(cpf))
    return digits.zfill(11) if digits else None

def parse_valor(val):
    if pd.isna(val):
        return None
    s = str(val).strip().replace(",", ".")
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except Exception:
        return None

def main():
    print("Lendo CSV")
    df = pd.read_csv(CSV_PATH, encoding="latin1", sep=";")
    df.columns = df.columns.str.strip().str.upper()  # normaliza colunas
    print(f"{len(df)} linhas lidas.")

    session = SessionLocal()
    inserted = 0

    for idx, row in df.iterrows():
        # CPF
        cpf_raw = safe_str(row.get("CPF"))
        cpf = normalize_cpf(cpf_raw) or f"NOCPF_{idx}"
        print(f"Inserindo linha {idx+1} CPF {cpf}")

        # Servidor
        nome = safe_str(row.get("NOME_SERVIDOR")) or "SEM NOME"
        escolaridade_ser = safe_str(row.get("ESCOLARIDADE_SERVIDOR"))
        situacao = safe_str(row.get("SITUACAO_SERVIDOR"))

        servidor = session.query(Servidor).filter_by(cpf=cpf).one_or_none()
        if not servidor:
            servidor = Servidor(
                cpf=cpf,
                nome=nome,
                escolaridade=escolaridade_ser,
                situacao=situacao
            )
            session.add(servidor)
            session.flush()

        # Orgão de exercício
        org_ex_nome = safe_str(row.get("ORGAO_EXERCICIO"))
        uf_uorg = safe_str(row.get("UF_UORG_EXERCICIO"))
        org_ex = Orgao(nome=org_ex_nome, uf=uf_uorg) if org_ex_nome else None
        if org_ex:
            session.add(org_ex)
            session.flush()

        # Unidade de exercício
        uorg_ex_nome = safe_str(row.get("UORG_EXERCICIO"))
        uorg_ex = Unidade(
            nome=uorg_ex_nome,
            uf=uf_uorg,
            orgao_id=org_ex.id if org_ex else None
        ) if uorg_ex_nome else None
        if uorg_ex:
            session.add(uorg_ex)
            session.flush()

        # UPAG
        upag_nome = safe_str(row.get("UPAG"))
        uf_upag = safe_str(row.get("UF_UPAG"))
        upag = Unidade(nome=upag_nome, uf=uf_upag) if upag_nome else None
        if upag:
            session.add(upag)
            session.flush()

        # Cargo
        cargo_nome = safe_str(row.get("CARGO"))
        pos = Cargo(title=cargo_nome, escolaridade=safe_str(row.get("ESCOLARIDADE_CARGO"))) if cargo_nome else None
        if pos:
            session.add(pos)
            session.flush()

        # Cargo origem
        cargo_origem_nome = safe_str(row.get("CARGO_ORIGEM"))
        pos_origem = Cargo(
            title=cargo_origem_nome,
            escolaridade=safe_str(row.get("ESCOLARIDADE_CARGO_ORIGEM"))
        ) if cargo_origem_nome else None
        if pos_origem:
            session.add(pos_origem)
            session.flush()

        # Orgão origem
        org_origem_nome = safe_str(row.get("ORGAO_ORIGEM"))
        org_origem = Orgao(nome=org_origem_nome) if org_origem_nome else None
        if org_origem:
            session.add(org_origem)
            session.flush()

        # Gratificação
        nome_rubrica = safe_str(row.get("NOME_RUBRICA"))
        nivel = safe_str(row.get("NIVEL_GRATIFICACAO"))
        valor = parse_valor(row.get("VALOR"))

        grat = Gratificacao(
            servidor_id=servidor.id,
            cargo_id=pos.id if pos else None,
            org_exercicio_id=org_ex.id if org_ex else None,
            uorg_exercicio_id=uorg_ex.id if uorg_ex else None,
            upag_id=upag.id if upag else None,
            org_origem_id=org_origem.id if org_origem else None,
            nome_rubrica=nome_rubrica,
            nivel_gratificacao=nivel,
            valor=valor
        )
        session.add(grat)
        inserted += 1

        # Commit a cada 500 registros
        if inserted % 500 == 0:
            session.commit()
            print(f"Commited {inserted} registros")

    session.commit()
    print(f"Importação finalizada. {inserted} gratificações inseridas.")
    session.close()

if __name__ == "__main__":
    main()
