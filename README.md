# Prateleira — o estoque que avisa

Sistema web de controle de estoque para pequenos comerciantes: cadastre produtos, registre entradas e saídas
e seja avisado antes que algo acabe.

**Autor:** Kagio Miura Neto — RM 559212
**Curso:** Engenharia de Computação, 3º ano · **Disciplina:** Engenharia de Software · **Professor:** Hercules Ramos
**Entrega:** Checkpoint 6 — Entrega Final

## Funcionalidades

- Login com senha armazenada em hash
- Cadastro, edição e remoção de produtos (SKU único, categoria, preço, estoque mínimo)
- Entradas e saídas de estoque com motivo e registro de quem fez
- Bloqueio de saída maior que o saldo disponível
- Painel com total de produtos, unidades, valor em estoque e lista "Repor em breve"
- Busca por nome, código ou categoria
- Histórico de movimentos com filtro de entradas e saídas
- Exportação do estoque em CSV (abre no Excel)

## Tecnologias

Python 3.12 · Flask · SQLite · Jinja2 · Gunicorn · Docker · pytest

## Instalar e rodar com Docker (recomendado)

Pré-requisito: Docker com Docker Compose.

```bash
git clone <URL-DO-REPOSITORIO>
cd prateleira
docker compose up --build
```

Abra http://localhost:5000 e entre com:

| Usuário | Senha |
|---------|-------|
| `admin` | `admin123` |

Os dados ficam no volume Docker `dados` e sobrevivem a reinícios.

Para definir usuário, senha e chave próprios (antes da primeira execução):

```bash
ADMIN_USER=maria ADMIN_PASSWORD=outra-senha SECRET_KEY=uma-chave-longa docker compose up --build
```

Para apagar tudo e recomeçar: `docker compose down -v`.

## Rodar sem Docker

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Acesse http://localhost:5000.

## Testes

```bash
pytest -q
```

12 testes cobrindo login, cadastro, saldo, bloqueio de saída, alerta de estoque baixo, histórico, busca e exportação.

## Variáveis de ambiente

| Variável | Padrão | Descrição |
|----------|--------|-----------|
| `ADMIN_USER` | `admin` | Usuário criado na primeira execução |
| `ADMIN_PASSWORD` | `admin123` | Senha desse usuário |
| `SECRET_KEY` | valor de desenvolvimento | Chave de assinatura da sessão (troque em produção) |
| `DATABASE_PATH` | `data/prateleira.db` | Caminho do banco SQLite |
| `PORT` | `5000` | Porta ao rodar com `python app.py` |

## Estrutura do projeto

```
app.py                  rotas, regras de negócio e banco de dados
templates/              telas (Jinja2)
static/style.css        identidade visual
tests/test_app.py       testes automatizados
docs/                   documentação final
Dockerfile
docker-compose.yml
requirements.txt
```

## Documentação

1. [Documentação do projeto: problema, requisitos, escopo, marca e pitch](docs/01-documentacao.md)
2. [Diagramas UML](docs/02-uml.md)
3. [Manual de uso](docs/03-manual-de-uso.md)
4. [Registro da jornada](docs/04-jornada.md)
5. [Papel do autor e teste de instalação](docs/05-papeis-e-teste-de-instalacao.md)

## Licença e uso

Projeto acadêmico desenvolvido para a FIAP. © 2026 Kagio Miura Neto.