from models_db import Base, engine

def main():
    print("Criando tabelas do banco de dados")
    Base.metadata.create_all(bind = engine)
    print("Tabelas criadas com sucesso")

if __name__ == "__main__":
    main()