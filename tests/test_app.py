import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import create_app, parse_preco  # noqa: E402


@pytest.fixture()
def client(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "t.db"), "TESTING": True,
                      "ADMIN_USER": "admin", "ADMIN_PASSWORD": "segredo"})
    c = app.test_client()
    return c


def login(c):
    return c.post("/login", data={"usuario": "admin", "senha": "segredo"}, follow_redirects=True)


def novo(c, sku="A1", nome="Arroz 5kg", preco="25,90", minimo="5"):
    return c.post("/produtos/novo", data={"sku": sku, "nome": nome, "categoria": "Mercearia",
                                          "preco": preco, "estoque_minimo": minimo}, follow_redirects=True)


def test_parse_preco():
    assert parse_preco("12,50") == 1250
    assert parse_preco("R$ 1.234,56") == 123456
    assert parse_preco("7.5") == 750
    with pytest.raises(ValueError):
        parse_preco("abc")


def test_exige_login(client):
    r = client.get("/produtos")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_login_invalido(client):
    r = client.post("/login", data={"usuario": "admin", "senha": "errada"})
    assert "incorretos" in r.get_data(as_text=True)


def test_cadastro_e_listagem(client):
    login(client)
    r = novo(client)
    assert "Arroz 5kg" in r.get_data(as_text=True)
    assert "R$ 25,90" in r.get_data(as_text=True)


def test_sku_duplicado(client):
    login(client)
    novo(client)
    r = novo(client)
    assert r.status_code == 400 and "Já existe" in r.get_data(as_text=True)


def test_entrada_saida_e_saldo(client):
    login(client)
    novo(client)
    client.post("/produtos/1/movimentar", data={"tipo": "entrada", "quantidade": "10"})
    client.post("/produtos/1/movimentar", data={"tipo": "saida", "quantidade": "3", "motivo": "venda"})
    html = client.get("/").get_data(as_text=True)
    assert "<strong>7</strong>" in html  # unidades em estoque


def test_saida_maior_que_estoque_e_bloqueada(client):
    login(client)
    novo(client)
    client.post("/produtos/1/movimentar", data={"tipo": "entrada", "quantidade": "2"})
    r = client.post("/produtos/1/movimentar", data={"tipo": "saida", "quantidade": "5"}, follow_redirects=True)
    assert "Saída maior que o estoque" in r.get_data(as_text=True)
    assert client.get("/movimentos").get_data(as_text=True).count("−5") == 0


def test_alerta_estoque_baixo(client):
    login(client)
    novo(client, minimo="5")
    client.post("/produtos/1/movimentar", data={"tipo": "entrada", "quantidade": "3"})
    assert "Repor em breve" in client.get("/").get_data(as_text=True)
    assert "Arroz 5kg" in client.get("/").get_data(as_text=True)


def test_remocao_preserva_historico(client):
    login(client)
    novo(client)
    client.post("/produtos/1/movimentar", data={"tipo": "entrada", "quantidade": "4"})
    client.post("/produtos/1/excluir", follow_redirects=True)
    assert "Nenhum produto cadastrado" in client.get("/produtos").get_data(as_text=True)
    assert "Arroz 5kg" in client.get("/movimentos").get_data(as_text=True)


def test_edicao_e_busca(client):
    login(client)
    novo(client)
    client.post("/produtos/1/editar", data={"sku": "A1", "nome": "Arroz 1kg", "categoria": "Mercearia",
                                            "preco": "6,00", "estoque_minimo": "2"})
    assert "Arroz 1kg" in client.get("/produtos?q=arroz").get_data(as_text=True)
    assert "Nenhum produto encontrado" in client.get("/produtos?q=zzz").get_data(as_text=True)


def test_exportar_csv(client):
    login(client)
    novo(client)
    r = client.get("/exportar.csv")
    assert r.mimetype == "text/csv" and "Arroz 5kg" in r.get_data(as_text=True)


def test_health(client):
    assert client.get("/health").json == {"status": "ok"}
