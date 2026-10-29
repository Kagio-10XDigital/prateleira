# 3. Manual de uso

## Instalar
Veja o [README](../README.md): com Docker, basta `docker compose up --build` e abrir http://localhost:5000.

## Primeiro acesso
Entre com **admin / admin123**. Troque a senha definindo `ADMIN_PASSWORD` antes de subir pela primeira vez.

## Tarefas do dia a dia
**Cadastrar um produto** — Produtos → *Novo produto*. Preencha código (SKU, único), nome, categoria, preço (ex.: 12,50) e estoque mínimo. Salve.

**Dar entrada (chegou mercadoria)** — Em Produtos, na linha do item, digite a quantidade, escreva um motivo se quiser (ex.: "compra fornecedor X") e clique em *Entrada*.

**Dar saída (vendeu ou perdeu)** — Mesma linha, quantidade e *Saída*. Se a quantidade for maior que o estoque, o sistema avisa e não registra.

**Ver o que repor** — A tela *Resumo* lista em "Repor em breve" os produtos com estoque igual ou abaixo do mínimo. Amarelo = baixo, vermelho = zerado.

**Procurar um item** — Campo de busca na tela Produtos (nome, código ou categoria).

**Ver o histórico** — Movimentos mostra data, produto, quantidade, motivo e quem registrou. Filtre por Entradas ou Saídas.

**Exportar** — Produtos → *Exportar CSV* (separador ponto e vírgula, abre direto no Excel).

**Editar ou remover** — *Editar* altera os dados do produto. *Remover* tira da lista, mas o histórico de movimentos é mantido.

## Problemas comuns
| Mensagem | O que fazer |
|----------|-------------|
| "Já existe um produto com esse código (SKU)" | Use outro código ou edite o produto existente. |
| "Preço inválido" | Escreva só números, com vírgula nos centavos: 12,50. |
| "Saída maior que o estoque" | Confira o saldo; registre antes a entrada pendente. |
| Página não abre | Confirme que o container está rodando: `docker compose ps`. |
