# 4. Registro da jornada

**Autor:** Kagio Miura Neto — RM 559212

## Contexto da entrega
O projeto foi desenvolvido individualmente. A entrega concentra-se no Checkpoint 6 (produto final).
O conteúdo que seria do CP4 (ideia, requisitos, UML, marca, pitch) e do CP5 (fluxos principais) está consolidado
na documentação final: `docs/01-documentacao.md` e `docs/02-uml.md`.

## Evolução do escopo (ideia → mínimo viável → produto)
| Etapa | O que define a etapa | Onde está no projeto |
|-------|----------------------|----------------------|
| Ideia | Problema do pequeno comerciante, persona, requisitos RF/RNF, marca e pitch | `docs/01-documentacao.md` |
| Mínimo viável | Fluxo central: cadastrar produto → registrar entrada/saída → ver saldo e alerta | RF02, RF04, RF06, RF07 |
| Produto final | Persistência real, login, busca, histórico, exportação CSV, testes, instalação por Docker | Todo o repositório |

## Decisões técnicas
| Decisão | Motivo |
|---------|--------|
| Flask + SQLite | Simples de instalar e explicar, sem servidor de banco separado; suficiente para um pequeno comércio. |
| Telas renderizadas no servidor (Jinja2) | Menos código, funciona em celular antigo, sem build de front-end. |
| Preço em centavos (inteiro) | Evita erro de arredondamento com números decimais. |
| Remoção lógica (campo `ativo`) | Mantém o histórico de movimentos consistente. |
| Movimento + saldo na mesma transação | Garante que saldo e histórico nunca divergem. |
| Docker | Instalação em um comando, igual em qualquer máquina. |
| Usuário único por ambiente | Mantém o escopo viável para um desenvolvedor; vários perfis ficam para versões futuras. |

## Mudanças de escopo
- **Mantido:** cadastro, movimentos, alerta de estoque baixo, painel, busca, histórico.
- **Incluído na versão final:** exportação CSV, senha com hash, testes automatizados.
- **Adiado:** leitura de código de barras, múltiplos usuários/perfis, múltiplas lojas, integração com nota fiscal.

## Dificuldades técnicas e como foram resolvidas
1. **Saldo negativo com movimentos simultâneos.** Duas saídas ao mesmo tempo podiam deixar o estoque negativo. Solução: movimento e saldo na mesma transação (`BEGIN IMMEDIATE`), validação antes de gravar e `CHECK (estoque_atual >= 0)` no banco.
2. **Erro de arredondamento nos preços.** Valores decimais (`float`) geram erros como 12,499999. Solução: guardar em centavos (inteiro) e converter na exibição, aceitando "12,50", "12.50" e "R$ 1.234,56".
3. **Remover produto sem perder histórico.** Apagar o registro quebraria os movimentos antigos (chave estrangeira). Solução: remoção lógica com `ativo = 0`.
4. **Código (SKU) duplicado.** Solução: `UNIQUE` no banco e tratamento de `IntegrityError` com mensagem clara em vez de tela de erro.
5. **Dados perdidos ao recriar o container.** O SQLite some junto com o container. Solução: volume Docker montado em `/data` e caminho do banco configurável por variável de ambiente.
6. **Garantir que as regras continuam funcionando.** Alterar uma tela podia quebrar o cálculo sem aviso. Solução: 12 testes automatizados (pytest) cobrindo login, cadastro, saldo, bloqueio de saída, histórico, busca e exportação.

## Aprendizados
- Regras de negócio críticas (saldo) devem ser protegidas em mais de uma camada: aplicação e banco.
- Escopo enxuto e bem documentado vale mais do que muitas funções incompletas.
- Empacotar com Docker elimina a maior parte dos problemas de instalação.
