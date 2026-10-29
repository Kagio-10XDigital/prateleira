# 2. Diagramas UML

## 2.1 Casos de uso
```mermaid
flowchart LR
    U([Comerciante])
    subgraph Prateleira
      UC1(Entrar no sistema)
      UC2(Cadastrar produto)
      UC3(Editar / remover produto)
      UC4(Registrar entrada)
      UC5(Registrar saída)
      UC6(Consultar painel e alertas)
      UC7(Buscar produtos)
      UC8(Consultar histórico)
      UC9(Exportar CSV)
    end
    U --- UC1 & UC2 & UC3 & UC4 & UC5 & UC6 & UC7 & UC8 & UC9
    UC4 -. exige .-> UC1
    UC5 -. valida saldo .-> UC6
```

## 2.2 Classes (modelo de domínio)
```mermaid
classDiagram
    class Usuario {
        +int id
        +string usuario
        +string senha_hash
    }
    class Produto {
        +int id
        +string sku
        +string nome
        +string categoria
        +int preco_centavos
        +int estoque_minimo
        +int estoque_atual
        +bool ativo
        +estoqueBaixo() bool
    }
    class Movimento {
        +int id
        +string tipo  // entrada | saida
        +int quantidade
        +string motivo
        +datetime criado_em
    }
    Usuario "1" --> "0..*" Movimento : registra
    Produto "1" --> "0..*" Movimento : possui
```

## 2.3 Sequência — registrar saída de estoque
```mermaid
sequenceDiagram
    actor C as Comerciante
    participant UI as Tela Produtos
    participant A as Flask (movimentar)
    participant DB as SQLite
    C->>UI: informa quantidade e clica em "Saída"
    UI->>A: POST /produtos/{id}/movimentar
    A->>A: valida sessão e quantidade > 0
    A->>DB: BEGIN IMMEDIATE; lê produto
    DB-->>A: estoque_atual
    alt estoque_atual - quantidade < 0
        A->>DB: ROLLBACK
        A-->>UI: aviso "Saída maior que o estoque"
    else saldo suficiente
        A->>DB: UPDATE produtos (novo saldo)
        A->>DB: INSERT movimentos
        A->>DB: COMMIT
        A-->>UI: aviso "Saída registrada. Estoque agora: N"
    end
```

## 2.4 Atividade — ciclo de reposição
```mermaid
flowchart TD
    A([Início]) --> B[Abrir painel]
    B --> C{Há produtos com<br/>estoque baixo?}
    C -- Não --> Z([Fim])
    C -- Sim --> D[Ver lista 'Repor em breve']
    D --> E[Comprar com o fornecedor]
    E --> F[Receber mercadoria]
    F --> G[Registrar entrada]
    G --> H[Saldo atualizado e alerta some]
    H --> Z
```

## 2.5 Modelo de dados (ER)
```mermaid
erDiagram
    USUARIOS ||--o{ MOVIMENTOS : registra
    PRODUTOS ||--o{ MOVIMENTOS : possui
    USUARIOS { int id PK
      string usuario UK
      string senha_hash }
    PRODUTOS { int id PK
      string sku UK
      string nome
      string categoria
      int preco_centavos
      int estoque_minimo
      int estoque_atual
      int ativo }
    MOVIMENTOS { int id PK
      int produto_id FK
      string tipo
      int quantidade
      string motivo
      string usuario
      string criado_em }
```
