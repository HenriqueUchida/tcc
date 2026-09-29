---
description: Documenta o desenvolvimento do TCC, incluindo arquitetura,
  decisões, implementação, testes, resultados e limitações, sem inventar
  informações.
name: tcc-documentation
---

# TCC Documentation

## Objetivo

Produzir documentação técnica e acadêmica baseada no estado real do
projeto.

A documentação deve explicar não apenas o que foi implementado, mas
também por que as decisões foram tomadas.

## Fontes de informação

Priorizar:

1.  código existente;
2.  `AGENTS.md`;
3.  `docs/estado_projeto.md`;
4.  `docs/arquitetura.md`;
5.  `docs/decisoes.md`;
6.  `docs/testes.md`;
7.  histórico Git;
8.  resultados experimentais fornecidos pelo usuário.

## Regra fundamental

Nunca inventar:

-   resultados;
-   métricas;
-   precisão;
-   desempenho;
-   testes;
-   validações;
-   funcionalidades.

Se algo foi planejado mas ainda não implementado, escrever como
planejamento.

Se algo foi implementado mas ainda não validado experimentalmente,
deixar isso explícito.

Utilizar `[A VALIDAR]` quando necessário.

## Linguagem

Utilizar linguagem acadêmica clara.

Evitar marketing.

Evitar afirmar que uma solução é "a melhor" sem critério experimental.

Explicar limitações.

## Estrutura recomendada

Ao documentar uma funcionalidade:

### Objetivo

Qual problema ela resolve.

### Funcionamento

Como o fluxo ocorre.

### Implementação

Quais módulos e tecnologias participam.

### Decisão técnica

Por que a abordagem foi escolhida.

### Testes

Como foi verificada.

### Resultados

Somente resultados realmente medidos.

### Limitações

O que ainda não foi resolvido.

## Reconhecimento facial

Diferenciar:

-   cadastro facial;
-   geração do vetor;
-   armazenamento no pgvector;
-   reconhecimento;
-   reidentificação.

## Tracking

Explicar que `track_id` é temporário.

Relacionar tracking à sessão sem afirmar que o tracker conhece a
identidade sozinho.

## Reidentificação

Diferenciar reidentificação por regras/contexto de eventual Person Re-Identification (ReID). ReID deve ser documentado como planejado, implementado ou validado conforme o estado real, sem afirmar ganho de desempenho sem experimento.

## Eventos de retirada

Documentar eventos como fatos observados pelo módulo dos nichos. Não atribuir identidade ao evento sem evidência/contrato de correlação. Timestamp é evidência importante, mas não deve ser descrito como chave única sem validação.

## Sessões

Explicar:

``` text
id_morador → identidade
id_sessao  → visita
track_id   → acompanhamento temporário
```

## Documentação do TCC

Quando solicitado a transformar documentação técnica em texto acadêmico:

-   manter precisão técnica;
-   não esconder limitações;
-   não inventar resultados;
-   explicar decisões;
-   utilizar termos consistentes em todo o documento.

## Regra de código

Não modificar código quando a tarefa for exclusivamente documental.

Caso seja encontrada uma inconsistência entre documentação e código,
registrar a inconsistência e solicitar ou sugerir a correção adequada.
