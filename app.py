"""Prateleira - controle de estoque para pequeno comércio.

Aplicação Flask + SQLite. Execute com:  python app.py
"""
import csv
import io
import os
import sqlite3
from datetime import datetime
from functools import wraps

from flask import (Flask, Response, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

SCHEMA = """
CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario TEXT NOT NULL UNIQUE,
    senha_hash TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sku TEXT NOT NULL UNIQUE,
    nome TEXT NOT NULL,
    categoria TEXT NOT NULL DEFAULT 'Geral',
    preco_centavos INTEGER NOT NULL CHECK (preco_centavos >= 0),
    estoque_minimo INTEGER NOT NULL DEFAULT 0 CHECK (estoque_minimo >= 0),
    estoque_atual INTEGER NOT NULL DEFAULT 0 CHECK (estoque_atual >= 0),
    ativo INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS movimentos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    tipo TEXT NOT NULL CHECK (tipo IN ('entrada','saida')),
    quantidade INTEGER NOT NULL CHECK (quantidade > 0),
    motivo TEXT NOT NULL DEFAULT '',
    usuario TEXT NOT NULL,
    criado_em TEXT NOT NULL
);
"""


def parse_preco(texto):
    """Converte '12,50' ou '12.50' em centavos (1250). Levanta ValueError."""
    limpo = (texto or "").strip().replace("R$", "").replace(" ", "")
    if "," in limpo:
        limpo = limpo.replace(".", "").replace(",", ".")
    valor = round(float(limpo) * 100)
    if valor < 0:
        raise ValueError("preço negativo")
    return int(valor)


def create_app(config=None):
    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("SECRET_KEY", "troque-esta-chave-em-producao"),
        DATABASE=os.environ.get("DATABASE_PATH", "data/prateleira.db"),
        ADMIN_USER=os.environ.get("ADMIN_USER", "admin"),
        ADMIN_PASSWORD=os.environ.get("ADMIN_PASSWORD", "admin123"),
    )
    if config:
        app.config.update(config)

    # ---------- banco ----------
    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
            g.db.execute("PRAGMA foreign_keys = ON")
        return g.db

    @app.teardown_appcontext
    def close_db(_exc):
        db = g.pop("db", None)
        if db is not None:
            db.close()

    def init_db():
        pasta = os.path.dirname(app.config["DATABASE"])
        if pasta:
            os.makedirs(pasta, exist_ok=True)
        db = sqlite3.connect(app.config["DATABASE"])
        db.executescript(SCHEMA)
        existe = db.execute("SELECT 1 FROM usuarios WHERE usuario = ?",
                            (app.config["ADMIN_USER"],)).fetchone()
        if not existe:
            db.execute("INSERT INTO usuarios (usuario, senha_hash) VALUES (?, ?)",
                       (app.config["ADMIN_USER"],
                        generate_password_hash(app.config["ADMIN_PASSWORD"])))
        db.commit()
        db.close()

    init_db()

    # ---------- auth ----------
    def login_required(view):
        @wraps(view)
        def wrapped(*a, **kw):
            if "usuario" not in session:
                return redirect(url_for("login", next=request.path))
            return view(*a, **kw)
        return wrapped

    @app.template_filter("brl")
    def brl(centavos):
        s = f"{centavos / 100:,.2f}"
        return "R$ " + s.replace(",", "X").replace(".", ",").replace("X", ".")

    @app.template_filter("data_br")
    def data_br(iso):
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            u = request.form.get("usuario", "").strip()
            row = get_db().execute("SELECT * FROM usuarios WHERE usuario = ?", (u,)).fetchone()
            if row and check_password_hash(row["senha_hash"], request.form.get("senha", "")):
                session.clear()
                session["usuario"] = row["usuario"]
                destino = request.args.get("next", "")
                return redirect(destino if destino.startswith("/") and not destino.startswith("//") else url_for("dashboard"))
            flash("Usuário ou senha incorretos. Confira os dados e tente de novo.", "erro")
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/health")
    def health():
        return {"status": "ok"}

    # ---------- dashboard ----------
    @app.route("/")
    @login_required
    def dashboard():
        db = get_db()
        resumo = db.execute(
            """SELECT COUNT(*) AS itens,
                      COALESCE(SUM(estoque_atual),0) AS unidades,
                      COALESCE(SUM(estoque_atual * preco_centavos),0) AS valor
               FROM produtos WHERE ativo = 1""").fetchone()
        baixos = db.execute(
            """SELECT * FROM produtos WHERE ativo = 1 AND estoque_atual <= estoque_minimo
               ORDER BY (estoque_atual - estoque_minimo), nome""").fetchall()
        recentes = db.execute(
            """SELECT m.*, p.nome FROM movimentos m JOIN produtos p ON p.id = m.produto_id
               ORDER BY m.id DESC LIMIT 8""").fetchall()
        return render_template("dashboard.html", resumo=resumo, baixos=baixos, recentes=recentes)

    # ---------- produtos ----------
    @app.route("/produtos")
    @login_required
    def produtos():
        q = request.args.get("q", "").strip()
        sql = "SELECT * FROM produtos WHERE ativo = 1"
        params = []
        if q:
            sql += " AND (nome LIKE ? OR sku LIKE ? OR categoria LIKE ?)"
            params = [f"%{q}%"] * 3
        sql += " ORDER BY nome"
        itens = get_db().execute(sql, params).fetchall()
        return render_template("produtos.html", itens=itens, q=q)

    def ler_formulario():
        f = request.form
        erros = []
        sku, nome = f.get("sku", "").strip(), f.get("nome", "").strip()
        categoria = f.get("categoria", "").strip() or "Geral"
        if not sku:
            erros.append("Informe o código (SKU).")
        if not nome:
            erros.append("Informe o nome do produto.")
        try:
            preco = parse_preco(f.get("preco", ""))
        except ValueError:
            preco = 0
            erros.append("Preço inválido. Use o formato 12,50.")
        try:
            minimo = int(f.get("estoque_minimo", "0") or 0)
            if minimo < 0:
                raise ValueError
        except ValueError:
            minimo = 0
            erros.append("O estoque mínimo deve ser um número inteiro maior ou igual a zero.")
        return dict(sku=sku, nome=nome, categoria=categoria, preco_centavos=preco,
                    estoque_minimo=minimo), erros

    @app.route("/produtos/novo", methods=["GET", "POST"])
    @login_required
    def produto_novo():
        if request.method == "POST":
            dados, erros = ler_formulario()
            if not erros:
                try:
                    db = get_db()
                    db.execute("""INSERT INTO produtos (sku, nome, categoria, preco_centavos, estoque_minimo)
                                  VALUES (:sku, :nome, :categoria, :preco_centavos, :estoque_minimo)""", dados)
                    db.commit()
                    flash(f"Produto “{dados['nome']}” cadastrado.", "ok")
                    return redirect(url_for("produtos"))
                except sqlite3.IntegrityError:
                    erros.append("Já existe um produto com esse código (SKU).")
            for e in erros:
                flash(e, "erro")
            return render_template("produto_form.html", p=dados, novo=True), 400
        return render_template("produto_form.html", p={}, novo=True)

    def buscar_produto(pid):
        p = get_db().execute("SELECT * FROM produtos WHERE id = ? AND ativo = 1", (pid,)).fetchone()
        if p is None:
            abort(404)
        return p

    @app.route("/produtos/<int:pid>/editar", methods=["GET", "POST"])
    @login_required
    def produto_editar(pid):
        atual = buscar_produto(pid)
        if request.method == "POST":
            dados, erros = ler_formulario()
            if not erros:
                try:
                    db = get_db()
                    dados["id"] = pid
                    db.execute("""UPDATE produtos SET sku=:sku, nome=:nome, categoria=:categoria,
                                  preco_centavos=:preco_centavos, estoque_minimo=:estoque_minimo WHERE id=:id""", dados)
                    db.commit()
                    flash("Produto atualizado.", "ok")
                    return redirect(url_for("produtos"))
                except sqlite3.IntegrityError:
                    erros.append("Já existe um produto com esse código (SKU).")
            for e in erros:
                flash(e, "erro")
            return render_template("produto_form.html", p=dados, novo=False, pid=pid), 400
        return render_template("produto_form.html", p=atual, novo=False, pid=pid)

    @app.route("/produtos/<int:pid>/excluir", methods=["POST"])
    @login_required
    def produto_excluir(pid):
        p = buscar_produto(pid)
        db = get_db()
        db.execute("UPDATE produtos SET ativo = 0 WHERE id = ?", (pid,))  # preserva histórico
        db.commit()
        flash(f"“{p['nome']}” foi removido da lista. O histórico de movimentos continua guardado.", "ok")
        return redirect(url_for("produtos"))

    # ---------- movimentos ----------
    @app.route("/produtos/<int:pid>/movimentar", methods=["POST"])
    @login_required
    def movimentar(pid):
        db = get_db()
        tipo = request.form.get("tipo")
        motivo = request.form.get("motivo", "").strip()
        try:
            qtd = int(request.form.get("quantidade", ""))
            if qtd <= 0 or tipo not in ("entrada", "saida"):
                raise ValueError
        except ValueError:
            flash("Informe uma quantidade inteira maior que zero.", "erro")
            return redirect(url_for("produtos"))
        try:
            db.execute("BEGIN IMMEDIATE")
            p = db.execute("SELECT * FROM produtos WHERE id = ? AND ativo = 1", (pid,)).fetchone()
            if p is None:
                db.rollback()
                abort(404)
            novo = p["estoque_atual"] + (qtd if tipo == "entrada" else -qtd)
            if novo < 0:
                db.rollback()
                flash(f"Saída maior que o estoque: “{p['nome']}” tem só {p['estoque_atual']} un.", "erro")
                return redirect(url_for("produtos"))
            db.execute("UPDATE produtos SET estoque_atual = ? WHERE id = ?", (novo, pid))
            db.execute("""INSERT INTO movimentos (produto_id, tipo, quantidade, motivo, usuario, criado_em)
                          VALUES (?, ?, ?, ?, ?, ?)""",
                       (pid, tipo, qtd, motivo, session["usuario"], datetime.now().isoformat(timespec="seconds")))
            db.commit()
        except sqlite3.Error:
            db.rollback()
            flash("Não foi possível registrar o movimento. Tente novamente.", "erro")
            return redirect(url_for("produtos"))
        verbo = "Entrada" if tipo == "entrada" else "Saída"
        flash(f"{verbo} de {qtd} un. registrada em “{p['nome']}”. Estoque agora: {novo}.", "ok")
        return redirect(request.referrer or url_for("produtos"))

    @app.route("/movimentos")
    @login_required
    def movimentos():
        tipo = request.args.get("tipo", "")
        sql = """SELECT m.*, p.nome, p.sku FROM movimentos m JOIN produtos p ON p.id = m.produto_id"""
        params = []
        if tipo in ("entrada", "saida"):
            sql += " WHERE m.tipo = ?"
            params.append(tipo)
        sql += " ORDER BY m.id DESC LIMIT 200"
        return render_template("movimentos.html", itens=get_db().execute(sql, params).fetchall(), tipo=tipo)

    @app.route("/exportar.csv")
    @login_required
    def exportar():
        linhas = get_db().execute(
            """SELECT sku, nome, categoria, preco_centavos, estoque_atual, estoque_minimo
               FROM produtos WHERE ativo = 1 ORDER BY nome""").fetchall()
        buf = io.StringIO()
        w = csv.writer(buf, delimiter=";")
        w.writerow(["sku", "nome", "categoria", "preco", "estoque_atual", "estoque_minimo"])
        for r in linhas:
            w.writerow([r["sku"], r["nome"], r["categoria"], f"{r['preco_centavos']/100:.2f}".replace(".", ","),
                        r["estoque_atual"], r["estoque_minimo"]])
        return Response("\ufeff" + buf.getvalue(), mimetype="text/csv",
                        headers={"Content-Disposition": "attachment; filename=estoque.csv"})

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
