# Decisões arquiteturais

Este documento registra decisões técnicas relevantes para o
desenvolvimento do TCC.

------------------------------------------------------------------------

## DEC-001 --- Separação entre reconhecimento facial e tracking

### Contexto

A câmera utilizada para reconhecimento facial na entrada é diferente das
câmeras responsáveis pelo monitoramento interno do mercado.

### Decisão

Separar as responsabilidades.

A câmera de entrada utilizará reconhecimento facial para determinar o
`id_morador`.

As câmeras internas utilizarão YOLO/Tracking para acompanhar pessoas.

### Motivo

Reconhecimento facial responde à identidade.

Tracking responde ao acompanhamento temporal de uma detecção.

Misturar as duas responsabilidades aumentaria o custo computacional e
dificultaria a arquitetura.

### Consequência

Será necessário possuir uma camada capaz de associar:

``` text
id_morador
    ↓
id_sessao
    ↓
track_id
```

------------------------------------------------------------------------

## DEC-002 --- `track_id` não representa identidade

### Contexto

O identificador produzido por um tracker é temporário e pode mudar.

### Decisão

O sistema nunca utilizará `track_id` como identidade permanente.

### Motivo

Uma mesma pessoa pode receber diferentes `track_id` em situações de:

-   perda do tracking;
-   mudança de câmera;
-   reentrada no campo de visão;
-   reinicialização do tracker.

### Consequência

A identidade será representada por `id_morador`.

------------------------------------------------------------------------

## DEC-003 --- Sessão como entidade persistente

### Contexto

Uma visita ao mercado pode possuir múltiplos tracks.

### Decisão

Criar `id_sessao` para representar a visita do morador.

### Motivo

A sessão permite manter a continuidade da compra mesmo quando o tracking
muda.

### Consequência

A estrutura lógica passa a ser:

``` text
id_morador
    ↓
id_sessao
    ↓
track atual
```

------------------------------------------------------------------------

## DEC-004 --- Estado temporário em memória

### Contexto

O sistema precisa acompanhar tracks em tempo real.

### Decisão

Utilizar estruturas em memória, como `dict`, para manter o estado atual
dos tracks.

### Motivo

A quantidade esperada de pessoas é pequena e a estrutura possui baixo
custo de memória.

O custo computacional principal está no processamento de visão
computacional.

### Consequência

O banco não será atualizado a cada frame.

Somente eventos relevantes serão persistidos.

------------------------------------------------------------------------

## DEC-005 --- Não finalizar sessão apenas pela perda do track

### Contexto

Um track pode desaparecer temporariamente devido a oclusão ou falha de
detecção.

### Decisão

A perda de tracking não será suficiente para finalizar uma sessão.

### Motivo

Finalizar a compra nesse momento poderia gerar cobrança incorreta.

### Consequência

O sistema deverá possuir uma lógica de reidentificação e confirmação de
saída.

------------------------------------------------------------------------

## DEC-006 --- Câmera de entrada dedicada

### Contexto

O reconhecimento facial e o acompanhamento interno possuem necessidades
diferentes.

### Decisão

Utilizar uma câmera específica para identificação na entrada.

### Motivo

A entrada fornece um evento natural para identificação e criação da
sessão.

Também evita a necessidade de reconhecimento facial contínuo durante
toda a compra.

### Consequência

A identidade inicial será obtida antes do acompanhamento interno.

------------------------------------------------------------------------

## DEC-007 --- PostgreSQL + pgvector

### Contexto

O sistema precisa armazenar vetores faciais e realizar busca por
similaridade.

### Decisão

Utilizar PostgreSQL com pgvector.

### Motivo

Permite manter os dados de negócio e os vetores no mesmo sistema de
persistência.

Para o protótipo inicial, a quantidade de moradores é pequena.

### Consequência

A necessidade de otimização por índice vetorial poderá ser reavaliada
conforme a escala do sistema.

------------------------------------------------------------------------

## DEC-008 --- Cadastro facial separado do reconhecimento

### Contexto

O cadastro de um morador não ocorre continuamente.

### Decisão

Separar:

``` text
cadastro_faces.py
```

do processo de reconhecimento.

### Motivo

Cadastro e reconhecimento possuem ciclos de vida diferentes.

### Consequência

O cadastro gera e armazena o vetor.

O reconhecimento apenas utiliza os vetores já cadastrados.

------------------------------------------------------------------------

## DEC-009 --- Configuração por `.env`

### Contexto

O sistema precisa de credenciais para acessar o PostgreSQL.

### Decisão

Utilizar variáveis de ambiente carregadas por `.env`.

### Motivo

Evitar credenciais diretamente no código.

### Consequência

`.env` deve permanecer fora do controle de versão.

------------------------------------------------------------------------

## DEC-010 --- Desenvolvimento incremental

### Contexto

O projeto possui várias partes complexas:

-   reconhecimento;
-   tracking;
-   múltiplas câmeras;
-   reidentificação;
-   produtos;
-   balanças;
-   saída;
-   cobrança.

### Decisão

Implementar as funcionalidades em etapas.

### Ordem prevista

``` text
Reconhecimento
    ↓
Sessão
    ↓
Tracking
    ↓
Associação
    ↓
Reidentificação
    ↓
Múltiplas câmeras
    ↓
Produtos
    ↓
Saída
    ↓
Cobrança
```

### Motivo

Permitir validação individual das partes e reduzir complexidade durante
o desenvolvimento.

------------------------------------------------------------------------

## DEC-011 --- Evitar complexidade prematura

### Contexto

O protótipo será executado em ambiente local e possui quantidade pequena
de usuários.

### Decisão

Não utilizar inicialmente:

-   microserviços;
-   Redis;
-   Kafka;
-   RabbitMQ;
-   Kubernetes;
-   arquitetura distribuída.

### Motivo

Não existe requisito atual que justifique essa complexidade.

### Consequência

O sistema permanecerá inicialmente como uma aplicação Python modular.

A arquitetura poderá ser revisada caso testes demonstrem necessidade.

------------------------------------------------------------------------

## DEC-012 --- Documentação baseada no estado real

### Contexto

O desenvolvimento ocorre simultaneamente à elaboração do TCC.

### Decisão

Manter documentação técnica durante o desenvolvimento.

### Motivo

Evitar perda das decisões e facilitar a elaboração das seções
acadêmicas.

### Consequência

Alterações relevantes devem atualizar:

-   `docs/estado_projeto.md`;
-   `docs/arquitetura.md`;
-   `docs/decisoes.md`;
-   `docs/testes.md`, quando aplicável.

------------------------------------------------------------------------

## DEC-013 --- Separação entre as duas câmeras do módulo do aluno

### Contexto

O módulo de visão do aluno utilizará duas câmeras com responsabilidades diferentes: uma câmera de entrada para reconhecimento facial e uma câmera interna para monitoramento e tracking.

### Decisão

As fontes de vídeo deverão possuir identificação e função explícitas, por exemplo:

```text
camera_entrada → ENTRADA
camera_interna → INTERNA
```

O código deverá selecionar o pipeline de processamento conforme a função da câmera.

### Motivo

Reconhecimento facial de entrada e tracking interno possuem objetivos e custos diferentes. Misturar os fluxos aumenta a complexidade e pode fazer uma câmera executar processamento que não deveria executar.

### Consequência

A configuração das câmeras passa a ser parte da arquitetura. Não depender de índices ou da ordem de abertura das câmeras.

------------------------------------------------------------------------

## DEC-014 --- Separação entre câmeras do aluno e ESP32-CAM dos nichos

### Contexto

Existem três ESP32-CAM, uma por nicho, implementadas no módulo do colega para detectar eventos de retirada de produtos.

### Decisão

As três ESP32-CAM serão tratadas como fontes de eventos de retirada, e não como câmeras de reconhecimento facial do módulo do aluno.

O evento deverá carregar informações observáveis pelo módulo de retirada, como nicho, produto, quantidade e timestamp. A identidade do morador e a sessão serão resolvidas pela camada de integração.

### Motivo

Separar responsabilidades permite que o módulo do colega seja desenvolvido e testado independentemente do reconhecimento/tracking.

### Consequência

Será necessário definir posteriormente um contrato de integração e uma estratégia de correlação entre evento de retirada e contexto da pessoa.

------------------------------------------------------------------------

## DEC-015 --- Timestamp como evidência de correlação, não como chave única

### Contexto

Os eventos de retirada serão registrados com data e hora. O módulo de tracking também terá informações temporais sobre a presença da pessoa em determinada zona/nicho.

### Decisão

O timestamp será uma das principais evidências para correlacionar uma retirada com uma sessão, mas não será utilizado isoladamente.

A correlação poderá considerar timestamp, nicho/zona, contexto do track e outras evidências disponíveis.

### Motivo

Duas pessoas podem estar no mercado ou próximas do mesmo nicho em horários semelhantes. Utilizar apenas o horário pode produzir associações incorretas.

### Consequência

O sistema deverá admitir estados como evento pendente/ambíguo quando não houver evidência suficiente para uma associação confiável.

------------------------------------------------------------------------

## DEC-016 --- ReID como estratégia futura de reidentificação

### Contexto

O tracking pode ser perdido durante a movimentação pelo mercado. Características visuais de aparência podem auxiliar na recuperação da identidade de um novo track.

### Decisão

Person Re-Identification (ReID) será considerado uma estratégia futura, após a implementação e medição do tracking básico.

Quando utilizado, ReID será tratado como evidência de aparência e combinado, quando possível, com tempo, posição/zona e movimento.

### Motivo

ReID adiciona custo computacional e complexidade. Não há justificativa para introduzi-lo antes de conhecer as limitações reais do tracking inicial.

### Consequência

A arquitetura deve permitir futura inclusão de ReID sem torná-lo uma dependência obrigatória da primeira versão.
