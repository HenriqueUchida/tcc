# Estado atual do projeto

Última atualização: 2026-09-28

## Objetivo

Desenvolver um protótipo de mercado autônomo para condomínio, capaz de identificar moradores, acompanhar sua movimentação, receber eventos de retirada e associar esses eventos a uma sessão de compra.

------------------------------------------------------------------------

## 1. Câmeras e fontes de vídeo

### Câmeras do módulo do aluno

O módulo do aluno utiliza duas câmeras:

| Fonte | Função | Estado |
|---|---|---|
| `camera_entrada` | reconhecimento facial na entrada | [x] definido conceitualmente |
| `camera_interna` | monitoramento e tracking | [x] definido conceitualmente |

Pendências:

- [ ] definir configuração concreta das fontes de vídeo;
- [ ] criar abstração/configuração de câmera;
- [ ] garantir identificação por `camera_id`/`camera_role`;
- [ ] implementar abertura e encerramento independentes;
- [ ] validar resolução/FPS adequados para cada pipeline.

### Câmeras do módulo do colega

Existem três ESP32-CAM, uma por nicho:

```text
ESP32-CAM N1
ESP32-CAM N2
ESP32-CAM N3
```

Responsabilidade prevista:

- detectar evento de retirada;
- identificar produto;
- determinar quantidade;
- registrar timestamp/evento.

Estado:

- [x] arquitetura conceitual definida;
- [ ] contrato de evento definido em conjunto;
- [ ] integração com o módulo de identidade;
- [ ] estratégia de correlação validada.

------------------------------------------------------------------------

## 2. Banco de dados

### Concluído

- [x] PostgreSQL definido
- [x] pgvector definido
- [x] tabela `usuarios`
- [x] campo `vetor_facial vector(128)`
- [x] configuração por `.env`
- [x] conexão centralizada

### Em desenvolvimento

- [ ] tabela de sessões integrada ao fluxo
- [ ] persistência dos estados relevantes
- [ ] tabela de itens da sessão
- [ ] estrutura para eventos de retirada, após definição do contrato

### Futuro

- [ ] tabela de produtos
- [ ] relacionamento sessão → itens
- [ ] informações necessárias para cobrança

------------------------------------------------------------------------

## 3. Cadastro facial

### Concluído

- [x] pasta local para fotografias
- [x] identificação do nome pelo nome do arquivo
- [x] suporte a formatos comuns de imagem
- [x] geração de vetor facial de 128 dimensões
- [x] armazenamento no PostgreSQL/pgvector

### Pendências

- [ ] evitar duplicação de cadastro ao executar novamente
- [ ] atualização de cadastro existente
- [ ] validação mais completa das imagens

------------------------------------------------------------------------

## 4. Reconhecimento facial / câmera de entrada

### Objetivo

Identificar o morador no momento da entrada e fornecer a identidade inicial para criação da sessão.

Fluxo planejado:

```text
camera_entrada
→ rosto
→ vetor facial
→ PostgreSQL/pgvector
→ id_morador
→ sessão
```

### Concluído

- [x] carregamento de imagem
- [x] localização de rosto
- [x] geração do vetor facial
- [x] consulta por distância no pgvector
- [x] filtro de usuário ativo
- [x] limiar inicial de distância

### Pendências

- [ ] integrar câmera de entrada ao fluxo
- [ ] estratégia de reconhecimento orientada a eventos
- [ ] tratamento de múltiplos rostos
- [ ] confirmação de identidade
- [ ] testes sistemáticos de iluminação/distância
- [ ] definição experimental do limiar
- [ ] criação automática da sessão após identificação

------------------------------------------------------------------------

## 5. Câmera interna e tracking

### Objetivo

Monitorar o ambiente interno e acompanhar as pessoas por meio de YOLO/tracking.

Fluxo planejado:

```text
camera_interna
→ YOLO
→ pessoa detectada
→ track_id
→ contexto espacial/zona
→ associação com sessão
```

### Concluído

- [x] definição conceitual do tracking
- [x] geração de `track_id`

### Pendências

- [ ] implementar pipeline da câmera interna
- [ ] estrutura central de tracks
- [ ] incluir `camera_id` no contexto do track
- [ ] associação `track_id → id_morador`
- [ ] associação `track_id → id_sessao`
- [ ] contexto de zona/nicho
- [ ] timeout de tracks perdidos
- [ ] reidentificação
- [ ] validação de continuidade do tracking

------------------------------------------------------------------------

## 6. Sessões de compra

### Conceito

Uma sessão representa a visita de um morador ao mercado.

```text
id_morador
    ↓
id_sessao
    ↓
track atual
```

### Concluído

- [x] definição conceitual
- [x] tabela `sessoes_compra` planejada
- [x] SessionManager inicial

### Pendências

- [ ] criação automática
- [ ] associação com tracking
- [ ] recuperação após perda de track
- [ ] estado `TRACK_PERDIDO`
- [ ] confirmação de saída
- [ ] finalização

------------------------------------------------------------------------

## 7. Reidentificação / ReID

### Objetivo

Permitir que uma pessoa continue associada à mesma sessão mesmo quando seu `track_id` for perdido e um novo track for criado.

### Estado

- [x] arquitetura conceitual definida
- [ ] implementação básica de recuperação de identidade
- [ ] testes de perda/recuperação de track
- [ ] avaliar necessidade de Person Re-Identification
- [ ] medir custo computacional antes de adicionar ReID

### Diretriz

ReID não é requisito inicial. Primeiro validar o tracking básico. Caso seja necessário, utilizar aparência como uma evidência adicional, combinada com tempo, posição/zona e movimento.

------------------------------------------------------------------------

## 8. Correlação de eventos de retirada

### Objetivo

Associar um evento produzido por uma ESP32-CAM de nicho à sessão correta.

Evento conceitual:

```json
{
  "id_evento": 152,
  "nicho": 2,
  "produto_id": 37,
  "quantidade": 1,
  "timestamp": "2026-09-28T12:31:15.420"
}
```

### Estado

- [x] separação entre evento de retirada e identidade definida
- [x] timestamp identificado como evidência importante
- [x] nicho identificado como contexto espacial importante
- [ ] contrato definitivo com o módulo do colega
- [ ] estrutura de correlação
- [ ] tratamento de eventos ambíguos
- [ ] testes com múltiplas pessoas

------------------------------------------------------------------------

## 9. Detecção de produtos

### Estado

- [ ] não implementado no módulo do aluno

O módulo do colega possui a responsabilidade de produzir os eventos de retirada, conforme contrato ainda a definir.

------------------------------------------------------------------------

## 10. Balanças

### Estado

- [ ] não implementado

Futuro: integrar sensores/balanças caso façam parte da solução final para determinação de quantidade.

------------------------------------------------------------------------

## 11. Saída

### Estado

- [ ] não implementado

Não considerar:

```text
track perdido = pessoa saiu
```

A saída deverá ser confirmada antes da finalização da sessão.

------------------------------------------------------------------------

## 12. Cobrança

### Estado

- [ ] não implementado

Fluxo futuro:

```text
sessão finalizada
    ↓
eventos/itens consolidados
    ↓
quantidades
    ↓
valor
    ↓
cobrança
```

------------------------------------------------------------------------

## 13. Próximas prioridades

1. Integrar criação de sessão ao reconhecimento da `camera_entrada`.
2. Definir configuração/abstração das duas câmeras do módulo do aluno.
3. Implementar pipeline da `camera_interna`.
4. Implementar estrutura de gerenciamento de tracks.
5. Associar track a sessão.
6. Implementar contexto espacial/zona.
7. Implementar perda temporária de track.
8. Validar necessidade de reidentificação/ReID.
9. Definir contrato de eventos com o módulo das três ESP32-CAM.
10. Implementar correlação evento → sessão.
11. Implementar saída.
12. Implementar finalização.
13. Implementar cobrança.
