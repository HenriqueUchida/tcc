---
description: Desenvolve, depura, testa e refatora o código do TCC do mercado autônomo, respeitando reconhecimento facial, duas câmeras do módulo do aluno, tracking, sessões e integração com eventos de retirada.
name: tcc-development
---

# TCC Development

## Objetivo

Atuar como agente de desenvolvimento do software do TCC, preservando uma arquitetura simples, explicável e adequada ao escopo acadêmico.

## Antes de qualquer implementação

Leia obrigatoriamente:

1. `AGENTS.md`
2. `docs/estado_projeto.md`
3. `docs/arquitetura.md`

Leia `docs/decisoes.md` quando a tarefa modificar arquitetura, banco, câmeras, reconhecimento, tracking, sessões ou integração de eventos.

## Duas câmeras do módulo do aluno

O módulo do aluno possui duas fontes com responsabilidades distintas:

```text
camera_entrada → ENTRADA → reconhecimento facial
camera_interna → INTERNA → YOLO + tracking
```

A implementação deve diferenciar as fontes por configuração/role. Não depender da ordem de abertura ou de índices mágicos.

Antes de alterar o pipeline de vídeo, verificar como `camera_id` e `camera_role` estão representados.

Não executar automaticamente o pipeline de reconhecimento facial na `camera_interna` nem o pipeline de tracking interno na `camera_entrada`, salvo requisito explícito e documentado.

## Módulo das três ESP32-CAM

As três ESP32-CAM pertencem ao módulo do colega e representam os nichos. Elas produzem eventos de retirada, não identidade facial.

O agente não deve acoplar esse módulo ao reconhecimento/tracking sem um contrato de integração definido.

Um evento pode conter conceitualmente:

```text
id_evento
nicho
produto_id
quantidade
timestamp
```

## Processo de implementação

Para cada tarefa significativa:

1. Entender o requisito.
2. Identificar os módulos envolvidos.
3. Inspecionar a implementação existente.
4. Identificar impactos.
5. Propor uma solução simples.
6. Implementar.
7. Executar testes.
8. Corrigir problemas.
9. Verificar regressões.
10. Atualizar documentação.
11. Atualizar `docs/estado_projeto.md`.

## Regras arquiteturais

Separar:

```text
Face Recognition → quem é?
Camera Manager   → qual fonte e qual função?
YOLO Tracking    → qual pessoa está sendo acompanhada?
Contexto espacial→ onde a pessoa está?
Session Manager  → qual visita pertence a essa pessoa?
Evento de retirada→ o que foi retirado e quando?
Correlação       → qual sessão está relacionada ao evento?
Database         → o que precisa ser persistido?
```

Não transformar `track_id` em identidade persistente.

Não criar uma sessão nova automaticamente toda vez que um track mudar.

## Visão computacional

O reconhecimento facial deve ser utilizado de forma orientada a eventos sempre que possível.

Evitar reconhecimento facial em todos os frames.

O tracking da `camera_interna` pode operar continuamente, mas sua frequência deve ser ajustada por testes.

## Reidentificação e ReID

Primeiro implementar e medir o tracking básico. ReID é uma possibilidade futura, não requisito inicial.

Se ReID for introduzido:

- não executar em todos os frames sem justificativa;
- tratar aparência como evidência, não como verdade absoluta;
- combinar, quando possível, aparência, posição/zona, movimento e tempo;
- medir custo computacional e impacto na associação antes de adotá-lo como parte principal do fluxo.

## Banco de dados

Não consultar ou atualizar o banco desnecessariamente a cada frame.

Não persistir o estado de tracking a cada frame.

Persistir eventos relevantes, como:

- identificação;
- criação de sessão;
- associação de sessão;
- reidentificação;
- eventos de retirada quando o contrato estiver definido;
- alteração relevante de estado;
- finalização.

Não executar comandos destrutivos sem autorização explícita.

## Correlação de retirada

Não assumir que timestamp sozinho identifica o responsável por uma retirada.

Quando integrar eventos, considerar os dados disponíveis no contexto da pessoa, como:

```text
timestamp + nicho/zona + track/sessão + outras evidências
```

Se a evidência for insuficiente, preservar o estado como pendente/ambíguo em vez de inventar uma associação.

## Código

Preferir:

- funções pequenas;
- classes apenas quando agregarem responsabilidade clara;
- nomes descritivos;
- tratamento explícito de erros;
- código fácil de testar;
- comentários apenas quando explicarem decisões não óbvias.

Evitar abstrações prematuras, frameworks desnecessários, código duplicado e complexidade distribuída sem benefício.

## Mudanças de dependências

Antes de adicionar uma biblioteca:

1. Verificar se a funcionalidade já pode ser implementada com dependências existentes.
2. Justificar a nova dependência.
3. Atualizar `requirements.txt`.
4. Registrar a decisão quando relevante.

## Saída

Não finalizar uma sessão somente porque o track desapareceu. Considerar zona de saída, tempo desde último avistamento, possíveis oclusões e reidentificação.

## Critério de conclusão

Uma tarefa só é considerada concluída quando:

- código foi implementado;
- testes relevantes foram executados;
- erros conhecidos foram registrados;
- documentação foi atualizada quando necessário;
- `docs/estado_projeto.md` representa o estado real.
