# Diagrama de classes do domínio

Classes de domínio do Assinify (as entidades SQLAlchemy em `backend/app/models/`) com seus atributos principais e relacionamentos.

```mermaid
classDiagram
    direction LR

    class Usuario {
        +int id_usuario
        +string nome
        +string email
        +string senha_hash
        +string role
        +date data_cadastro
        +string foto_perfil
        +string moeda_base
        +datetime termos_aceitos_em
        +string termos_versao
        +salvar()
        +atualizar()
        +definir_foto()
        +deletar()
        +buscar_por_id()
        +to_dict()
    }

    class Categoria {
        +int id_categoria
        +string nome_categoria
        +string descricao
        +int id_usuario
        +salvar()
        +atualizar()
        +deletar()
        +listar_por_usuario()
        +buscar_por_id()
        +to_dict()
    }

    class Assinatura {
        +int id_assinatura
        +string nome_servico
        +decimal valor_mensal
        +string moeda
        +int num_pessoas
        +date data_renovacao
        +string status
        +date data_cancelamento
        +date teste_ate
        +string tipo_plano
        +string metodo_pagamento
        +string periodicidade
        +int id_usuario
        +int id_categoria
        +valor_minha_parte()
        +valor_anualizado()
        +anualizado_em()
        +em_teste()
        +proxima_renovacao()
        +renovacoes_no_periodo()
        +salvar()
        +atualizar()
        +deletar()
        +to_dict()
    }

    class HistoricoAssinatura {
        +int id
        +int id_assinatura
        +string campo
        +text valor_antigo
        +text valor_novo
        +datetime data_alteracao
        +int id_usuario
        +to_dict()
    }

    class TaxaCambio {
        +string moeda
        +decimal taxa_por_usd
        +datetime atualizada_em
    }

    Usuario "1" --> "0..*" Categoria : possui
    Usuario "1" --> "0..*" Assinatura : possui
    Categoria "1" --> "0..*" Assinatura : classifica
    Assinatura "1" --> "0..*" HistoricoAssinatura : registra alteracoes
    Usuario "1" --> "0..*" HistoricoAssinatura : autor da alteracao
    Assinatura ..> TaxaCambio : converte valores usando
```

## Relacionamentos

| Relação | Cardinalidade | Observação |
|---|---|---|
| `Usuario` possui `Categoria` | 1 para 0..* | Cascade `all, delete-orphan`: ao excluir o usuário, as categorias dele são apagadas. Cada usuário só enxerga as próprias. |
| `Usuario` possui `Assinatura` | 1 para 0..* | Cascade `all, delete-orphan`. |
| `Categoria` classifica `Assinatura` | 1 para 0..* | Uma categoria com assinaturas não pode ser excluída. |
| `Assinatura` registra `HistoricoAssinatura` | 1 para 0..* | Chave estrangeira com `ON DELETE SET NULL`: o histórico sobrevive à assinatura excluída. |
| `Usuario` é autor de `HistoricoAssinatura` | 1 para 0..* | Também `ON DELETE SET NULL`. |
| `Assinatura` usa `TaxaCambio` | dependência | Sem chave estrangeira: a taxa é buscada pela `moeda` (`app/cambio.py`) para converter o valor para a `moeda_base` do usuário. |
