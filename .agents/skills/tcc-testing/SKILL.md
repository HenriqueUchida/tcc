---
description: Planeja e executa testes do TCC, com foco em duas câmeras, reconhecimento facial, tracking, sessões, reidentificação e correlação de eventos.
name: tcc-testing
---

# TCC Testing

## Objetivo

Garantir que alterações no sistema possam ser verificadas de forma reproduzível.

## Antes dos testes

Ler:

1. `AGENTS.md`
2. `docs/estado_projeto.md`
3. código relacionado à funcionalidade testada.

## Testes de configuração das câmeras

Verificar explicitamente:

- `camera_entrada` utiliza o pipeline de reconhecimento facial;
- `camera_interna` utiliza o pipeline de tracking;
- as fontes são identificadas por `camera_id`/`camera_role`;
- a ordem das câmeras não altera suas responsabilidades;
- uma configuração inválida é rejeitada de forma clara.

## Categorias de teste

### Testes unitários

Priorizar componentes independentes:

- conexão/configuração;
- reconhecimento de vetor;
- configuração/identificação de câmera;
- SessionManager;
- transições de estado;
- associação track → sessão;
- correlação temporal/espacial quando implementada.

### Testes de integração

Verificar:

```text
camera_entrada
    ↓
reconhecimento
    ↓
id_morador
    ↓
sessão
    ↓
camera_interna
    ↓
tracking
    ↓
track/sessão
```

Quando o contrato de eventos estiver implementado:

```text
evento de retirada
    +
contexto do tracking
    ↓
correlação
    ↓
sessão + produto + quantidade
```

### Testes de visão computacional

Considerar:

- rosto frontal;
- rosto parcialmente oculto;
- diferentes distâncias;
- iluminação diferente;
- mais de uma pessoa na entrada;
- ausência de rosto;
- track perdido;
- novo track;
- pessoa atravessando zonas;
- reidentificação.

### Testes de reidentificação/ReID

Se ReID ainda não estiver implementado, testar apenas o comportamento arquitetural esperado após perda de track.

Quando implementado, avaliar também falsos positivos e custo computacional. Não assumir que similaridade visual garante identidade.

### Testes de sessão

Verificar:

- criação;
- associação;
- recuperação;
- perda temporária de tracking;
- reidentificação;
- finalização;
- tentativa de finalização indevida.

### Testes de eventos de retirada

Quando o módulo estiver integrado, considerar:

- evento com timestamp válido;
- evento com nicho válido;
- múltiplas retiradas;
- duas pessoas no mesmo nicho;
- ausência de candidato;
- candidatos múltiplos;
- evento fora da janela temporal;
- evento que não pode ser associado com segurança.

## Regra de saída

Perda de `track_id` não deve, sozinha, finalizar uma sessão.

## Resultados

Registrar resultados reais em `docs/testes.md`. Nunca criar números fictícios.

## Regressão

Depois de alterar reconhecimento, tracking, session manager, câmera ou banco, executar os testes relacionados às funcionalidades já existentes.

## Critério

Um teste deve ter:

- objetivo;
- entrada;
- procedimento;
- resultado esperado;
- resultado obtido;
- status.
