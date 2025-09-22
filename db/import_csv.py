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
    if cpf is None:
        return None
    digits = re.sub(r"[^\d]", "", str(cpf))
    return digits.zfill(11) if digits else None

def parse_valor(val):
    if pd.isna(val):
        return None
    s = str(val).strip().replace(",", ".")
    try:
        return Decimal(s).quantize(Decimal("0.01"))
    except Exception:
        return None

def get_or_create_orgao(session, nome, uf=None):
    """Busca ou cria órgão de forma segura"""
    if not nome:
        return None
    
    # Primeiro tenta buscar
    orgao = session.query(Orgao).filter_by(nome=nome).first()
    if orgao:
        return orgao
    
    # Se não existe, tenta criar
    try:
        orgao = Orgao(nome=nome, uf=uf)
        session.add(orgao)
        session.flush()
        return orgao
    except Exception:
        # Se deu erro de unique, busca novamente (pode ter sido criado por outra thread)
        session.rollback()
        orgao = session.query(Orgao).filter_by(nome=nome).first()
        if orgao:
            return orgao
        raise

def get_or_create_unidade(session, nome, uf=None, orgao_id=None):
    """Busca ou cria unidade de forma segura"""
    if not nome:
        return None
    
    # Busca considerando nome e orgao_id
    unidade = session.query(Unidade).filter_by(nome=nome, orgao_id=orgao_id).first()
    if unidade:
        return unidade
    
    # Se não existe, tenta criar
    try:
        unidade = Unidade(nome=nome, uf=uf, orgao_id=orgao_id)
        session.add(unidade)
        session.flush()
        return unidade
    except Exception:
        session.rollback()
        unidade = session.query(Unidade).filter_by(nome=nome, orgao_id=orgao_id).first()
        if unidade:
            return unidade
        raise

def get_or_create_cargo(session, title, escolaridade=None):
    """Busca ou cria cargo de forma segura"""
    if not title:
        return None
    
    cargo = session.query(Cargo).filter_by(title=title).first()
    if cargo:
        return cargo
    
    try:
        cargo = Cargo(title=title, escolaridade=escolaridade)
        session.add(cargo)
        session.flush()
        return cargo
    except Exception:
        session.rollback()
        cargo = session.query(Cargo).filter_by(title=title).first()
        if cargo:
            return cargo
        raise

def main():
    print("Lendo CSV")
    df = pd.read_csv(CSV_PATH, encoding="latin1", sep=";")
    df.columns = df.columns.str.strip().str.upper()
    print(f"{len(df)} linhas lidas.")

    session = SessionLocal()
    inserted = 0

    try:
        for idx, row in df.iterrows():
            if idx % 100 == 0:
                print(f"Processando linha {idx+1}/{len(df)}")
            
            # CPF
            cpf_raw = safe_str(row.get("CPF"))
            cpf = normalize_cpf(cpf_raw)
            
            if not cpf or cpf == "00000000000":
                cpf = f"NOCPF_{idx:06d}"
            
            print(f"Processando linha {idx+1} - CPF: {cpf}")

            # Servidor
            nome = safe_str(row.get("NOME_SERVIDOR")) or "SEM NOME"
            escolaridade_ser = safe_str(row.get("ESCOLARIDADE_SERVIDOR"))
            situacao = safe_str(row.get("SITUACAO_SERVIDOR"))

            servidor = session.query(Servidor).filter_by(cpf=cpf).first()
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
            org_ex = get_or_create_orgao(session, org_ex_nome, uf_uorg) if org_ex_nome else None

            # Unidade de exercício
            uorg_ex_nome = safe_str(row.get("UORG_EXERCICIO"))
            uorg_ex = get_or_create_unidade(
                session, uorg_ex_nome, uf_uorg, org_ex.id if org_ex else None
            ) if uorg_ex_nome else None

            # UPAG
            upag_nome = safe_str(row.get("UPAG"))
            uf_upag = safe_str(row.get("UF_UPAG"))
            upag = get_or_create_unidade(session, upag_nome, uf_upag) if upag_nome else None

            # Cargo
            cargo_nome = safe_str(row.get("CARGO"))
            pos = get_or_create_cargo(
                session, cargo_nome, safe_str(row.get("ESCOLARIDADE_CARGO"))
            ) if cargo_nome else None

            # Cargo origem
            cargo_origem_nome = safe_str(row.get("CARGO_ORIGEM"))
            pos_origem = get_or_create_cargo(
                session, cargo_origem_nome, safe_str(row.get("ESCOLARIDADE_CARGO_ORIGEM"))
            ) if cargo_origem_nome else None

            # Orgão origem
            org_origem_nome = safe_str(row.get("ORGAO_ORIGEM"))
            org_origem = get_or_create_orgao(session, org_origem_nome) if org_origem_nome else None

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
                cargo_origem_id=pos_origem.id if pos_origem else None,
                nome_rubrica=nome_rubrica,
                nivel_gratificacao=nivel,
                valor=valor
            )
            session.add(grat)
            inserted += 1

            if inserted % 50 == 0:
                session.commit()
                print(f"Commit realizado - {inserted} registros processados")

        session.commit()
        print(f"Importação finalizada. {inserted} gratificações inseridas.")

    except Exception as e:
        session.rollback()
        print(f"Erro na linha {idx+1}: {str(e)}")
        raise
    finally:
        session.close()

if __name__ == "__main__":
    main()