# Weblue

E-commerce de cosméticos desenvolvido para o projeto de
Laboratório de Inovação III.

## Tecnologias

- Python
- FastAPI
- MySQL
- SQLAlchemy
- HTML
- CSS
- JavaScript
- Git / GitHub
- Railway

## Funcionalidades

### RF-001 — Cadastro de Cliente
- Cadastro de novos clientes
- Validação de nome, e-mail, CPF e telefone
- Validação de senha
- Verificação de CPF e e-mail duplicados
- Armazenamento seguro da senha utilizando hash

### RF-002 — Login
- Autenticação por e-mail e senha
- Verificação da senha armazenada
- Redirecionamento para o perfil do cliente
- Tratamento de credenciais inválidas

### RF-003 — Recuperação de Senha
- Tela de recuperação implementada
- Validação da nova senha
- Fluxo de recuperação em desenvolvimento
- Token temporário de recuperação: pendente

### Perfil do Cliente
- Exibição de nome
- E-mail
- CPF
- Telefone
- Opção de logout

## Arquitetura

Frontend (HTML/CSS/JavaScript)
        ↓
Fetch API
        ↓
HTTP/HTTPS + JSON
        ↓
FastAPI
        ↓
SQLAlchemy
        ↓
MySQL

## Segurança

- Senhas protegidas com hash Argon2/Pwdlib
- Validação de dados no frontend e backend
- Arquivos de ambiente protegidos pelo `.gitignore`
- Token de autenticação: em desenvolvimento
- Token de recuperação de senha: pendente

## Localização dos Artefatos

- **Repositório GitHub:** https://github.com/matdavidbs-gif/WeBlue.git
- **Branch principal:** `main`
- **Banco de dados:** Concluído
- **API / Swagger:** Concluído
- **Cadastro:** Concluído
- **Login:** Concluído
- **Perfil:** Implementado
- **Recuperação de senha:** Parcial
- **Deploy Railway:** Em desenvolvimento
- **Demonstração:** Pendente
