# 1. Documentação do projeto

**Autor:** Kagio Miura Neto — RM 559212 · Disciplina: Engenharia de Software · Prof. Hercules Ramos

## 1.1 Problema e público-alvo
Donos de pequenos comércios (mercadinhos, papelarias, lojas de bairro) controlam o estoque em caderno ou planilha.
Resultado: produto que acaba sem ninguém perceber, venda perdida, compra de reposição no escuro e capital parado em itens encalhados.

**Persona — Dona Marta, 52 anos, mercadinho de bairro.** Usa celular e um computador antigo, não tem tempo para sistemas complicados,
quer saber "o que preciso comprar hoje" em menos de 10 segundos.

## 1.2 Solução
O **Prateleira** é um sistema web simples: cadastra produtos, registra entradas e saídas, calcula o saldo automaticamente
e destaca o que está abaixo do estoque mínimo.

## 1.3 Requisitos funcionais
| ID | Requisito |
|----|-----------|
| RF01 | O sistema deve exigir login (usuário e senha) para qualquer acesso. |
| RF02 | O usuário deve cadastrar produtos com SKU único, nome, categoria, preço de venda e estoque mínimo. |
| RF03 | O usuário deve editar e remover produtos (remoção preserva o histórico). |
| RF04 | O usuário deve registrar entradas e saídas de estoque com quantidade e motivo opcional. |
| RF05 | O sistema deve impedir saídas maiores que o estoque disponível. |
| RF06 | O sistema deve calcular o saldo de cada produto a cada movimento. |
| RF07 | O sistema deve destacar produtos com estoque menor ou igual ao mínimo (painel e lista). |
| RF08 | O painel deve mostrar total de produtos, unidades, valor em estoque e últimos movimentos. |
| RF09 | O usuário deve buscar produtos por nome, SKU ou categoria. |
| RF10 | O usuário deve consultar o histórico de movimentos, filtrando por entrada/saída. |
| RF11 | O usuário deve exportar o estoque em CSV (abre no Excel). |

## 1.4 Requisitos não funcionais
| ID | Requisito |
|----|-----------|
| RNF01 | **Usabilidade:** tarefas principais em até 3 cliques; textos em português simples; mensagens de erro dizem como corrigir. |
| RNF02 | **Segurança:** senhas armazenadas com hash; sessão assinada; rotas protegidas; consultas SQL parametrizadas. |
| RNF03 | **Persistência:** dados em SQLite, mantidos entre reinícios (volume Docker). |
| RNF04 | **Integridade:** movimento e atualização de saldo ocorrem na mesma transação; saldo nunca fica negativo (CHECK no banco). |
| RNF05 | **Portabilidade:** executa em qualquer máquina com Docker, ou com Python 3.12. |
| RNF06 | **Responsividade:** interface utilizável em celular e desktop. |
| RNF07 | **Qualidade:** regras principais cobertas por testes automatizados (pytest). |
| RNF08 | **Acessibilidade:** foco visível, rótulos em campos, contraste adequado. |

## 1.5 Escopo
**Dentro (versão 1.0):** login de usuário único, cadastro de produtos, movimentos, alerta de estoque baixo, painel, busca, histórico, exportação CSV.

**Fora (versões futuras):** vários perfis de usuário, leitura de código de barras, múltiplas lojas, integração com PDV/nota fiscal,
previsão de demanda, aplicativo móvel nativo.

## 1.6 Marca
- **Nome:** Prateleira.
- **Logo:** etiqueta de preço amarela com a letra P.
- **Paleta:** azul-tinta `#14213D`, azul-prateleira `#1F4E79`, amarelo-etiqueta `#FFC857`, papel `#F6F7F9`; verde `#2E7D32` (ok) e vermelho `#B3261E` (zerado).
- **Tipografia:** fontes do sistema (system-ui) — carrega rápido e funciona offline.
- **Coerência com o público:** visual limpo, números grandes, cores de semáforo que a Dona Marta entende sem treinamento.
