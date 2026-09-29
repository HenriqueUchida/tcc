# Arquitetura do sistema

## 1. Visão geral

O sistema é um protótipo de mercado autônomo para condomínio baseado em visão computacional.

A arquitetura separa identidade, tracking, sessão, fontes de vídeo e eventos de retirada.

```text
Reconhecimento facial → QUEM é?
Tracking                → QUAL pessoa está sendo acompanhada?
Contexto espacial       → ONDE essa pessoa está?
Sessão                  → QUAL visita pertence a essa pessoa?
Evento de retirada      → O QUE foi retirado e QUANDO?
Correlação              → QUAL sessão está relacionada ao evento?
Banco de dados          → O QUE precisa ser persistido?
```

## 2. Câmeras e responsabilidades

O módulo do aluno utiliza **duas câmeras distintas**:

| Câmera | Função | Pipeline principal |
|---|---|---|
| `camera_entrada` | Identificação inicial | detecção facial → face recognition → `id_morador` |
| `camera_interna` | Monitoramento e tracking | YOLO → tracking → `track_id` → contexto espacial |

O código deve diferenciar as câmeras por configuração/identificador, e não pela posição na lista, índice arbitrário ou suposição de que a primeira câmera é sempre a entrada.

Exemplo conceitual:

```text
camera_entrada:
    role = ENTRADA

camera_interna:
    role = INTERNA
```

A câmera de entrada não deve ser usada automaticamente como câmera de tracking interno, e a câmera interna não deve executar reconhecimento facial continuamente apenas por ser uma fonte de vídeo.

Além dessas duas câmeras, o módulo do colega possui **três ESP32-CAM**, uma por nicho. Essas câmeras produzem eventos de retirada e não fazem parte, neste momento, do pipeline de reconhecimento facial do aluno.

## 3. Arquitetura geral

```text
                         ┌──────────────────────┐
                         │   CÂMERA DE ENTRADA  │
                         │      role=ENTRADA    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   FACE RECOGNITION   │
                         └──────────┬───────────┘
                                    │
                                    ▼
                              id_morador
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   SESSION MANAGER    │
                         └──────────┬───────────┘
                                    │
                                id_sessao
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   CÂMERA INTERNA     │
                         │      role=INTERNA    │
                         └──────────┬───────────┘
                                    │
                                    ▼
                            YOLO + TRACKING
                                    │
                                    ▼
                         track_id + zona/posição
                                    │
                  ┌─────────────────┴─────────────────┐
                  │                                   │
                  ▼                                   ▼
         CONTEXTO DA SESSÃO                 TRÊS ESP32-CAM
         pessoa + sessão + zona             N1 / N2 / N3
                  │                                   │
                  │                          eventos de retirada
                  │                                   │
                  └─────────────────┬─────────────────┘
                                    ▼
                              CORRELAÇÃO
                                    │
                                    ▼
                         sessão + produto + quantidade
                                    │
                                    ▼
                              Itens da sessão
                                    │
                                    ▼
                              Zona de saída
                                    │
                                    ▼
                           Finalização da sessão
                                    │
                                    ▼
                                Cobrança
```

## 4. Identidade, tracking e sessão

### Identidade

`id_morador` é persistente e representa a pessoa cadastrada.

### Tracking

`track_id` é temporário e pertence ao contexto de uma câmera/tracker. Ele pode mudar quando o tracking é perdido ou reiniciado.

### Sessão

`id_sessao` representa a visita ao mercado e pode sobreviver a mudanças de `track_id`.

```text
id_morador
    ↓
id_sessao
    ↓
track_id atual
```

## 5. Fluxo da câmera de entrada

```text
camera_entrada
    ↓
detecção de rosto
    ↓
face encoding
    ↓
consulta ao PostgreSQL/pgvector
    ↓
id_morador
    ↓
criação/recuperação de sessão
```

A câmera de entrada fornece a identidade inicial. O reconhecimento não deve ser executado continuamente sem necessidade.

## 6. Fluxo da câmera interna

```text
camera_interna
    ↓
YOLO
    ↓
detecção de pessoa
    ↓
tracker
    ↓
track_id
    ↓
contexto espacial/zona
    ↓
associação com sessão
```

O tracker não deve assumir que `track_id` é identidade permanente.

## 7. Perda e recuperação de tracking

A perda de um track pode ocorrer por oclusão, falha de detecção, mudança de área ou outros motivos.

```text
track_id perdido
      ↓
manter sessão temporariamente
      ↓
procurar evidências de recuperação
      ↓
novo track
      ↓
associação confiável
      ↓
mesma sessão
```

### ReID como possibilidade futura

Uma estratégia futura poderá utilizar Person Re-Identification para comparar características de aparência entre um novo track e tracks/sessões anteriormente observados.

A aparência deve ser tratada como **evidência**, não como identidade absoluta. A decisão de reidentificação poderá combinar:

- aparência/ReID;
- movimento;
- posição/zona;
- intervalo de tempo;
- outras evidências disponíveis.

ReID não faz parte da implementação inicial até que os testes demonstrem necessidade.

## 8. Eventos de retirada

Cada uma das três ESP32-CAM do módulo do colega representa um nicho.

O módulo do colega deve produzir eventos semelhantes a:

```json
{
  "id_evento": 152,
  "nicho": 2,
  "produto_id": 37,
  "quantidade": 1,
  "timestamp": "2026-09-28T12:31:15.420"
}
```

O contrato real deverá ser definido conjuntamente antes da integração.

O evento de retirada não precisa conhecer `id_morador` ou `id_sessao`.

## 9. Correlação entre pessoa e retirada

A integração deverá relacionar o evento de retirada ao contexto da pessoa.

O timestamp é uma informação importante, mas não deve ser tratado como chave única. A correlação poderá considerar:

```text
retirada
  ├── timestamp
  ├── nicho
  └── produto/quantidade

contexto da pessoa
  ├── id_sessao
  ├── track_id
  ├── timestamp
  └── zona/nicho

                 ↓
             correlação
                 ↓
          id_sessao + item
```

Se houver múltiplas pessoas candidatas e as evidências forem insuficientes, o sistema não deve inventar uma associação. O evento poderá permanecer pendente/ambíguo para tratamento posterior.

## 10. Estado temporário

O estado de tracking e contexto espacial deve permanecer em memória quando apropriado.

Exemplo conceitual:

```python
tracks = {
    17: {
        "camera_id": "camera_interna",
        "id_sessao": 42,
        "id_morador": 1,
        "zona": "N2",
        "status": "ATIVO"
    }
}
```

Não executar `UPDATE` no banco a cada frame.

## 11. Banco de dados

O PostgreSQL possui inicialmente as responsabilidades de:

- moradores;
- vetores faciais;
- sessões;
- posteriormente eventos/itens necessários ao negócio.

Alterações de schema devem ser registradas em `docs/database.md`.

## 12. Máquina de estados

```text
NÃO_IDENTIFICADO
        ↓
IDENTIFICADO
        ↓
EM_COMPRA
        ↓
TRACK_PERDIDO
        │
        ├────→ REIDENTIFICADO → EM_COMPRA
        │
        └────→ SAÍDA_CONFIRMADA
                       ↓
                  FINALIZADA
```

## 13. Princípio central

A arquitetura deve evitar que um único componente tente resolver tudo.

```text
Câmera de entrada → identidade
Câmera interna    → tracking/contexto espacial
ESP32-CAM         → evento de retirada
Sessão            → continuidade da visita
Correlação        → associação evento ↔ sessão
Banco             → persistência
```

Essa separação permite desenvolver e testar cada parte independentemente e reduz o risco de uma mudança em um módulo quebrar os demais.
