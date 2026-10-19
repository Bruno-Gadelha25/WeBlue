# Modelo de dados

## Entidades principais
- `clientes`
  - id, nome_completo, email, cpf, telefone, senha_hash, status, aceitou_termos_em, criado_em, atualizado_em
  - possui relação com `pedidos`.
- `produtos`
  - id, nome, descricao, preco, estoque, categoria, marca, imagem_url, status, data_criacao, data_atualizacao
- `pedidos`
  - id, cliente_id, status, valor_total, criado_em, atualizado_em
  - possui `itens` e referência a cliente.
- `itens_pedido`
  - id, pedido_id, produto_id, quantidade, preco_unitario, subtotal
- `administradores`
  - id, nome, email, senha_hash, ativo, data_criacao, data_atualizacao

## Relacionamentos observados
- `Cliente` -> `Pedido` (um para muitos)
- `Pedido` -> `ItemPedido` (um para muitos, com cascade delete-orphan)
- `ItemPedido` -> `Produto` (muitos para um, via `produto_id`)

## Resumo de entidades-chave
- `Cliente`: base do cadastro, autenticação, perfil e autorização de acesso.
- `Produto`: catálogo de cosméticos do e-commerce.
- `Pedido`: ciclo de compra e status do pedido.
- `ItemPedido`: composição do pedido com quantidade e subtotal.
- `Administrador`: autenticação separada para painel administrativo.

## Observações de persistência
- Os modelos são criados com `Base.metadata.create_all(bind=engine)` no início da aplicação.
- O projeto usa `BIGINT` em algumas chaves e `Numeric(10,2)` em preços.
- Há validação de unicidade em `email` e `cpf` no cadastro de cliente.
