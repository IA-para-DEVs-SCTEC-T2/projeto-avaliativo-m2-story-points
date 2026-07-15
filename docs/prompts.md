# Registro de Prompts — Agente de Story Points

Este arquivo documenta os principais prompts utilizados durante o planejamento, implementação e refinamento do agente.

---

## 1. Prompt de Validação da Issue (`validate_issue`)

**Objetivo:** Verificar se a issue possui informações técnicas e funcionais suficientes para que o agente consiga estimar o esforço com confiança.

```
Analise se esta issue contém informações suficientes para estimar esforço técnico:
DESCRIÇÃO: "{desc}"

Critérios mínimos:
1. Objetivo claro do que precisa ser feito
2. Contexto técnico ou dependências mencionadas
3. Critérios de aceitação ou detalhes funcionais

Responda EXATAMENTE neste formato:
VALIDO: SIM ou NAO
FALTA: [liste o que falta ou escreva 'NADA']
```

**Por que este formato:** A estrutura rígida (`VALIDO:` / `FALTA:`) facilita o parsing determinístico da resposta, evitando ambiguidade e tornando a validação confiável mesmo com modelos diferentes.

---

## 2. Prompt de Análise Técnica (`analyze_technical`)

**Objetivo:** Decompor a issue em etapas técnicas, classificar a complexidade e identificar riscos.

```
Como Engenheiro de Software Sênior, analise a issue abaixo:
ISSUE: "{desc}"

Forneça:
1. ETAPAS: Lista de tarefas técnicas necessárias (separadas por ; )
2. COMPLEXIDADE: BAIXA, MEDIA ou ALTA
3. RISCOS: Principais riscos técnicos ou de negócio (separados por ; )

Mantenha o formato exato:
ETAPAS: ...
COMPLEXIDADE: ...
RISCOS: ...
```

**Por que separador `;`:** Permite split simples e robusto, sem depender de quebra de linha ou numeração do modelo.

---

## 3. Prompt de Estimativa de Pontos (`estimate_points` — parte 1)

**Objetivo:** Obter um número único da escala Fibonacci com base nos dados já analisados.

```
Com base na análise técnica:
- Etapas: {len(steps)}
- Complexidade: {comp}
- Riscos: {len(risks)}

Aplique a escala Fibonacci de esforço: 1, 2, 3, 5, 8, 13
Regras rápidas:
1-2: Simples, sem riscos, poucas etapas
3-5: Média complexidade, integração interna
8: Complexa, riscos moderados, dependência externa
13: Alta incerteza, refatoração ou múltiplas integrações

Responda APENAS com o NÚMERO.
```

**Decisão de design:** Pedir apenas o número e extraí-lo via regex (`\b(13|8|5|3|2|1)\b`) é mais robusto do que pedir texto livre e tentar interpretar depois.

---

## 4. Prompt de Justificativa (`estimate_points` — parte 2)

**Objetivo:** Gerar uma explicação legível para o usuário final sobre o porquê da estimativa.

```
Escreva uma justificativa técnica concisa (máx. 4 linhas) para a estimativa de {points} Story Points.
Mencione: complexidade ({comp}), volume de etapas e riscos principais.
```

**Por que separado:** Manter o prompt de número e o de justificativa separados evita que o modelo "negocie" o número ao escrever a justificativa, mantendo a estimativa mais estável.

---

## 5. Prompts usados durante o desenvolvimento (planejamento e correção)

### 5.1 Planejamento inicial do fluxo
> "Preciso criar um agente LangGraph que recebe a descrição de uma issue de software e estima story points usando a escala Fibonacci. Quais nós fazem sentido nesse fluxo?"

### 5.2 Definição do estado compartilhado
> "Como devo estruturar o AgentState com TypedDict para armazenar validação, análise técnica e estimativa final de forma coerente com LangGraph?"

### 5.3 Refinamento do parsing
> "O parsing com split() encadeado é frágil quando o LLM usa Markdown. Como posso usar regex para torná-lo robusto a variações de formatação?"

### 5.4 Extração segura do número Fibonacci
> "Se o LLM responder '8 pontos' ou 'entre 5 e 8', como extrair apenas um valor válido da escala Fibonacci sem concatenar dígitos acidentalmente?"
