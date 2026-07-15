# 🎯 Agente de Estimativa de Story Points

Agente de IA construído com **LangGraph** que automatiza a estimativa de esforço de issues de software usando a escala Fibonacci, eliminando a subjetividade e o tempo gasto em planning poker.

---

## 📋 Descrição do Problema

Times de desenvolvimento perdem tempo significativo em reuniões de planning tentando estimar o esforço de cada issue. A estimativa é inconsistente porque depende da experiência individual de cada desenvolvedor e do nível de detalhe da descrição.

Este agente automatiza esse processo: recebe a descrição de uma issue, valida se ela tem informações suficientes, realiza uma análise técnica estruturada e devolve uma estimativa justificada em Story Points.

---

## 🤖 Objetivo do Agente

| | |
|---|---|
| **Entrada** | Descrição textual de uma issue (título + detalhes técnicos/funcionais) |
| **Processo** | Validação → Análise técnica → Estimativa → Relatório |
| **Saída** | Story Points (escala Fibonacci), nível de complexidade, riscos identificados e justificativa |

O sistema é considerado um **agente** porque toma decisões autônomas: decide se a issue é válida para estimativa, classifica a complexidade, identifica riscos e justifica a estimativa — tudo sem intervenção humana durante a execução.

---

## 🔄 Fluxo com LangGraph

```
Entrada (issue_description)
        ↓
  [ validar ]  ──── issue inválida ──→  END (retorna o que falta)
        │
   issue válida
        ↓
  [ analisar ]  →  etapas, complexidade, riscos
        ↓
  [ estimar ]   →  story_points, justificativa
        ↓
  [ salvar_relatorio ]  →  gera arquivo .md em results/
        ↓
       END
```

Cada nó é uma função Python que recebe e retorna partes do `AgentState`. O roteamento condicional após `validar` permite encerrar o fluxo cedo caso a issue esteja mal descrita.

---

## 🛠️ Ferramenta Integrada

**`save_report_tool`** — escrita de relatório técnico em arquivo Markdown.

- Gera um arquivo `.md` na pasta `results/` com a estimativa completa
- O nome do arquivo usa um hash da descrição da issue para evitar colisões
- Atualiza o estado do agente com o caminho do arquivo gerado
- Contribui para o rastreamento histórico das estimativas realizadas

---

## ⚙️ Como Executar

### Pré-requisitos
- Python 3.10+
- Conta na [Groq](https://console.groq.com) (gratuita) para obter a API key

### 1. Clone o repositório
```bash
git clone <url-do-repositorio>
cd projeto-avaliativo-m2-story-points
```

### 2. Crie e ative o ambiente virtual
```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Instale as dependências
```bash
pip install -r requirements.txt
```

### 4. Configure a chave de API
```bash
cp .env.example .env
```
Edite o arquivo `.env` e adicione sua chave Groq:
```
GROQ_API_KEY=gsk_sua_chave_aqui
```

### 5. Execute o agente
```bash
python main.py
```

---

## 📥 Exemplo de Entrada

```
Título: Implementar sistema de login com OAuth2 (Google)
Descrição:
- Criar tela de login com botão 'Entrar com Google'
- Configurar credenciais no Google Cloud Console
- Implementar fluxo OAuth2 no backend (Python/FastAPI)
- Salvar token de acesso e refresh token no banco de dados (PostgreSQL)
- Criar middleware de autenticação para proteger rotas privadas
- Adicionar testes unitários e de integração
```

## 📤 Exemplo de Saída

```
✅ Processamento concluído!
--------------------------------------------------
⭐ Story Points: 8
📊 Complexidade: ALTA
⚠️ Riscos: Segurança no fluxo OAuth2, Dependência de serviço externo (Google), Complexidade de testes de integração
📝 Etapas: 6 identificadas
💬 Justificativa:
A estimativa de 8 Story Points reflete a alta complexidade da integração OAuth2,
que envolve dependência externa (Google Cloud), implementação de segurança no
backend, persistência de tokens e cobertura de testes. O volume de 6 etapas
técnicas com riscos de segurança justifica o peso elevado.

✅ Relatório salvo em: results/estimativa_1234.md
```

---

## 🏗️ Estrutura do Projeto

```
projeto-avaliativo-m2-story-points/
├── main.py               # Ponto de entrada da aplicação
├── requirements.txt      # Dependências com versões fixadas
├── .env.example          # Modelo de variáveis de ambiente (sem valores reais)
├── .gitignore            # Ignora .env, __pycache__, .venv, results/
├── src/
│   ├── state.py          # Definição do AgentState (TypedDict)
│   ├── nodes.py          # Nós do grafo: validate_issue, analyze_technical, estimate_points
│   └── graph.py          # Montagem do grafo LangGraph + ferramenta save_report_tool
├── docs/
│   └── prompts.md        # Registro dos principais prompts utilizados
├── issues/               # Pasta para arquivos de issues de entrada (futuro)
└── results/              # Relatórios gerados pelo agente (criado em runtime)
```

---

## 🔑 Decisões Principais

| Decisão | Justificativa |
|---|---|
| **Groq + Llama 3 70B** | API gratuita, latência baixa, ótimo raciocínio estruturado sem custo |
| **Temperature 0.1** | Respostas mais determinísticas e consistentes para análise técnica |
| **Formato de resposta estruturado** | Reduz ambiguidade no parsing — o modelo responde com separadores fixos |
| **Regex para extração de número** | Mais robusto que `filter(str.isdigit)` — evita concatenar dígitos de textos como "5 a 8" |
| **Roteamento condicional** | Evita chamar o LLM 3 vezes para issues inválidas — encerra cedo e economiza tokens |
| **Hash no nome do arquivo** | Evita colisão de nomes sem depender de timestamp ou UUID externo |

---

## ⚠️ Limitações

- A estimativa depende da qualidade da descrição da issue — issues vagas serão rejeitadas
- O parsing da análise técnica assume que o LLM segue o formato solicitado; respostas muito fora do padrão caem no fallback
- O modelo Llama 3 70B via Groq tem limite de tokens por minuto na camada gratuita
- Não há persistência de histórico entre execuções (cada execução é independente)
- O agente não consulta o backlog ou issues anteriores para calibrar estimativas

---

## 🔒 Segurança

- Chaves de API armazenadas exclusivamente em `.env` (nunca versionado)
- `.env.example` contém apenas os nomes das variáveis, sem valores reais
- `.gitignore` configurado para ignorar `.env`, `results/`, `.venv/` e caches
