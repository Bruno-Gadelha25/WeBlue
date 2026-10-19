# Tech Stack

## Linguagem e runtime
- Python 3.x
- FastAPI como framework HTTP principal.
- SQLAlchemy como ORM e acesso ao banco.
- MySQL como banco de dados relacional.
- HTML, CSS e JavaScript no frontend estático.

## Dependências observadas
- `fastapi`: framework web principal.
- `sqlalchemy`: mapeamento ORM e sessões de banco.
- `pymysql`: driver para MySQL.
- `pydantic-settings`: leitura de configurações via `.env`.
- `jwt`: geração e validação de tokens JWT.
- `pwdlib`: hash de senhas com algoritmos seguros.
- `python-dotenv`/arquivo `.env` para configuração local.
- `railway` para deploy/hosting.

## Observações de runtime e configuração
- O backend usa `Settings` em `src/backend/app/config.py` para ler `db_user`, `db_password`, `db_host`, `db_port`, `db_name`, `jwt_secret_key`, `jwt_algorithm` e `jwt_expire_minutes`.
- O banco é configurado em `src/backend/app/database.py` com `mysql+pymysql` e `pool_pre_ping=True`.
- O CORS está habilitado em `src/backend/app/main.py` para localhost e ambiente Railway.

## Stack existente (como está no projeto)
- Backend: FastAPI + SQLAlchemy + MySQL
- Frontend: HTML + CSS + JavaScript
- Segurança: JWT + hashing de senha com `pwdlib`
- Deploy: Railway
