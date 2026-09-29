# Instruções dos agentes — TCC Mercado Autônomo

## 1. Contexto do projeto

Este projeto é o Trabalho de Conclusão de Curso (TCC) de Engenharia da Computação.

O objetivo é desenvolver um protótipo de mercado autônomo para condomínio. O sistema deverá identificar o morador na entrada, acompanhar sua movimentação dentro do mercado, receber eventos de retirada de produtos e associar esses eventos a uma sessão de compra. Ao final da permanência, a sessão deverá ser finalizada para posterior geração da cobrança.

O projeto possui dois módulos de visão sob responsabilidade do aluno e um módulo de eventos de retirada desenvolvido pelo colega:

### Câmeras sob responsabilidade do aluno

1. **Câmera de entrada** — dedicada ao reconhecimento facial e à identificação inicial do morador.
2. **Câmera interna** — dedicada ao monitoramento do ambiente e ao tracking das pessoas.

O código deve diferenciar explicitamente essas duas fontes de vídeo. Não assumir que qualquer câmera é intercambiável. A configuração da câmera deve informar sua função/role.

### Câmeras do módulo do colega

Existem **três ESP32-CAM**, uma por nicho/gôndola. Elas pertencem ao módulo de eventos de retirada. O módulo do colega detecta a ação de retirada e produz eventos contendo, conforme a implementação dele, informações como nicho, produto, quantidade e horário.

As ESP32-CAM dos nichos **não devem ser tratadas como câmeras de reconhecimento facial do módulo do aluno**. A integração entre os módulos será feita posteriormente por uma camada de correlação.

## 2. Tecnologias principais

- Python
- OpenCV
- face_recognition
- dlib
- Ultralytics YOLO
- PostgreSQL
- pgvector
- python-dotenv
- Git

## 3. Conceitos fundamentais

### id_morador

Identidade persistente do morador cadastrada no PostgreSQL.

### id_sessao

Identificador persistente da visita do morador ao mercado.

### track_id

Identificador temporário atribuído pelo algoritmo de tracking a uma pessoa em uma determinada fonte/câmera. `track_id` NÃO representa uma identidade permanente e não deve ser usado sozinho para identificar um morador.

### camera_id / camera_role

A fonte de vídeo deve ser identificável. No módulo do aluno, pelo menos:

```text
camera_entrada → role = ENTRADA
camera_interna → role = INTERNA
```

O código deve saber qual fluxo aplicar com base nessa configuração, em vez de depender de números mágicos ou da ordem em que as câmeras são abertas.

### evento de retirada

É produzido pelo módulo dos três nichos/ESP32-CAM e representa uma ação observada, por exemplo:

```text
id_evento
nicho
produto_id
quantidade
timestamp
```

Esse evento não deve carregar identidade facial por obrigação. A associação com uma sessão será responsabilidade da integração/correlação.

## 4. Arquitetura conceitual

```text
                 CÂMERA DE ENTRADA
                        ↓
                 FACE RECOGNITION
                        ↓
                   id_morador
                        ↓
                    id_sessao
                        ↓
                CÂMERA INTERNA
                        ↓
                 YOLO + TRACKING
                        ↓
             track_id + contexto espacial
                        ↓
                sessão/pessoa ativa
                        │
                        │
        ┌───────────────┴────────────────┐
        │                                │
        ▼                                ▼
MÓDULO DO ALUNO                  MÓDULO DO COLEGA
tracking/identidade              3 ESP32-CAM
sessão/localização               eventos de retirada
        │                                │
        └──────────────┬─────────────────┘
                       ▼
                 CORRELAÇÃO
                       ↓
              sessão + produto + quantidade
```

A correlação deve considerar, conforme os dados disponíveis, fatores como **timestamp, nicho/zona e contexto de tracking**. Não assumir que timestamp sozinho seja suficiente.

## 5. Reidentificação e aparência

A perda de um `track_id` não significa automaticamente que a pessoa saiu.

A arquitetura poderá futuramente utilizar características de aparência/Person Re-Identification (ReID) para auxiliar na recuperação de identidade após perda de tracking. Exemplos de evidências de aparência podem incluir características visuais aprendidas pelo modelo, e não apenas regras manuais como “camisa preta”.

**ReID é uma possibilidade arquitetural futura, não um requisito inicial.** Não implementar ou adicionar modelos ReID apenas por antecipação. Primeiro implementar e medir o tracking básico; posteriormente avaliar se a perda de identidade justifica o custo computacional adicional.

Quando ReID for utilizado, tratá-lo como evidência para reidentificação, não como verdade absoluta. Combinar, quando possível, aparência, movimento, posição/zona e tempo.

## 6. Responsabilidades

### recognition/

Responsável por:

- reconhecimento facial na câmera de entrada;
- processamento relacionado à identidade;
- componentes de visão necessários ao tracking interno;
- eventual reidentificação futura.

### tracking/

Responsável por:

- YOLO/tracker da câmera interna;
- `track_id`;
- estado temporário dos tracks;
- contexto espacial/zona;
- perda e recuperação de tracks.

### camera/

Responsável por:

- configuração das fontes de vídeo;
- identificação da câmera por `camera_id`/`camera_role`;
- abertura e encerramento das câmeras;
- impedir que o fluxo de entrada seja tratado como fluxo interno ou vice-versa.

### session/

Responsável por:

- criação de sessões;
- associação entre morador e sessão;
- associação entre track e sessão;
- estados da sessão;
- finalização da sessão.

### integration/ ou events/

Quando essa camada for criada, será responsável por:

- receber/interpretar eventos de retirada do módulo do colega;
- correlacionar evento de retirada com contexto de sessão;
- manter rastreabilidade da associação;
- não inventar uma associação quando as evidências forem insuficientes.

### database/

Responsável por:

- conexão com PostgreSQL;
- consultas;
- persistência;
- acesso ao banco.

### cadastro_faces.py

Responsável por carregar fotografias de cadastro, gerar vetores faciais e inserir/atualizar moradores no banco.

### reconhecimento.py

Pode orquestrar o fluxo principal, mas não deve concentrar toda a lógica de negócio. A abertura/configuração das duas câmeras e as responsabilidades de cada uma devem permanecer claramente separadas.

## 7. Princípios de desenvolvimento

1. Priorizar simplicidade.
2. Evitar complexidade prematura.
3. Não criar microserviços sem requisito.
4. Não introduzir Redis, Kafka, RabbitMQ, filas ou arquiteturas distribuídas sem necessidade demonstrada.
5. Não adicionar dependências sem justificar.
6. Não executar reconhecimento facial em todos os frames quando uma estratégia orientada a eventos for suficiente.
7. Não executar ReID em todos os frames sem necessidade e sem medição.
8. Não gravar o estado do tracking no banco a cada frame.
9. Manter estado temporário em memória quando apropriado.
10. Persistir eventos importantes para o negócio.
11. Não tratar `track_id` como identidade permanente.
12. Não finalizar sessão somente porque um track foi perdido.
13. Manter reconhecimento facial, tracking, gerenciamento de câmera e sessão como responsabilidades distintas.
14. Diferenciar explicitamente `camera_entrada` e `camera_interna` no código/configuração.
15. Não misturar as três ESP32-CAM do colega com o pipeline de reconhecimento/tracking do aluno sem um contrato de integração definido.
16. Priorizar código compreensível para apresentação acadêmica.
17. Toda mudança arquitetural relevante deve ser registrada em `docs/decisoes.md`.
18. O estado real do projeto deve ser mantido em `docs/estado_projeto.md`.

## 8. Banco de dados

O banco utiliza PostgreSQL com pgvector.

Tabela principal de moradores:

```sql
CREATE TABLE usuarios (
    id_morador SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    status_ativo BOOLEAN DEFAULT TRUE,
    vetor_facial vector(128)
);
```

Tabela de sessões planejada:

```sql
CREATE TABLE sessoes_compra (
    id_sessao SERIAL PRIMARY KEY,
    id_morador INTEGER NOT NULL,
    inicio TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fim TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'EM_ANDAMENTO',
    track_id_atual INTEGER,
    CONSTRAINT fk_sessao_morador
        FOREIGN KEY (id_morador)
        REFERENCES usuarios(id_morador)
);
```

Alterações estruturais no banco devem ser documentadas em `docs/database.md`.

## 9. Segurança e dados

As fotografias utilizadas para cadastro não devem ser versionadas no Git.

O arquivo `.env` não deve ser versionado.

Nunca inserir senhas ou credenciais diretamente no código.

Não adicionar dados pessoais reais desnecessários ao repositório.

## 10. Processo obrigatório antes de alterar código

Antes de implementar:

1. Ler este arquivo.
2. Ler `docs/estado_projeto.md`.
3. Ler `docs/arquitetura.md`.
4. Ler `docs/decisoes.md` quando a tarefa tiver impacto arquitetural.
5. Inspecionar os arquivos relacionados.
6. Verificar se já existe implementação semelhante.
7. Apresentar um plano curto quando a alteração for significativa.

Depois de implementar:

1. Executar testes.
2. Verificar regressões.
3. Atualizar documentação quando necessário.
4. Atualizar `docs/estado_projeto.md`.
5. Registrar decisão arquitetural quando aplicável.
6. Mostrar claramente quais arquivos foram alterados.

## 11. Regras de documentação

Nunca inventar métricas, taxas de reconhecimento, resultados de testes, desempenho, validações experimentais ou funcionalidades que ainda não existem.

Diferenciar:

- planejado;
- implementado;
- testado;
- validado experimentalmente.

Quando um resultado ainda não existir, utilizar `[A VALIDAR]`.

## 12. Git

Não executar `git push` automaticamente.

Antes de alterações grandes, verificar o estado do repositório.

Preferir commits pequenos e semanticamente claros.
