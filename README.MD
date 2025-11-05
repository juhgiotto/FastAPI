# Criação de uma API com FastAPI utilizando dados do dados.gov.br

## 📌 Visão Geral

Este repositório contém uma aplicação em Python construída com o framework FastAPI que consome dados públicos do portal Dados.gov.br e expõe uma API para consulta. O objetivo é demonstrar como montar uma API REST moderna, eficiente e documentada automaticamente.

## 🛠 Funcionalidades

* Uso do FastAPI para criação de endpoints HTTP.
* Consumo de conjuntos de dados públicos disponíveis no Dados.gov.br.
* Estrutura modular com diretórios `app/` (lógica da API) e `db/` (acesso ao(s) dado(s)).
* Documentação automática gerada pelo FastAPI (Swagger UI / Redoc).
* Dependências gerenciadas via `requirements.txt`.

## 📂 Estrutura do Projeto

```
├── app/             # Código da API (routers, modelos, serviços)  
├── db/              # Código de acesso ou tratamento dos dados públicos  
├── requirements.txt # Lista de dependências Python  
└── README.md        # (este arquivo)  
```

## 🔧 Como Executar

1. Clone este repositório:

   ```bash
   git clone https://github.com/juhgiotto/FastAPI.git  
   cd FastAPI  
   ```
2. Criar um ambiente virtual (recomendado):

   ```bash
   python3 -m venv venv  
   source venv/bin/activate       # no Linux/macOS  
   venv\Scripts\activate          # no Windows  
   ```
3. Instalar as dependências:

   ```bash
   pip install -r requirements.txt  
   ```
4. Executar a aplicação:

   ```bash
   uvicorn app.main:app --reload  
   ```

   Acesse a documentação automática em `http://127.0.0.1:8000/docs` ou `http://127.0.0.1:8000/redoc`.

## 📡 Endpoints Principais

* `GET /` – Health check ou endpoint raiz da API.
* Outros endpoints definidos no diretório `app/routers` para consumir os dados do Dados.gov.br.
  *(Você pode listar especificamente aqui os endpoints conforme implementados)*

## 📊 Sobre os Dados

Os dados utilizados são públicos, provenientes do portal Dados.gov.br, o qual centraliza diversas bases abertas de diversos órgãos. A aplicação consome esses dados e oferece acesso via API de forma simplificada.

## ✅ Por que usar FastAPI?

* Muito rápida e performática, com suporte a asyncio.
* Geração automática de documentação interativa (Swagger UI).
* Tipagem forte com pydantic, o que facilita validação e autocompletar.
* Ótimo para microserviços ou APIs escaláveis.

## 🎯 Possíveis Melhorias

* Inserir autenticação (JWT / OAuth2).
* Adicionar testes automatizados (pytest).
* Fazer deploy em ambiente de produção (ex: Docker + Kubernetes).
* Cache ou paginação para lidar com grandes volumes de dados.
* Monitoramento/Logging mais robusto.

## 👤 Autor

Feito por **Júlia Sernagiotto**.
Para dúvidas, melhorias ou contribuições, fique à vontade para abrir *issues* ou *pull requests*.

---

Se quiser, posso preparar também uma **badge**, **exemplo de Dockerfile**, ou **guia de contribuição** para o repositório. Você gostaria que eu adicionasse isso?
