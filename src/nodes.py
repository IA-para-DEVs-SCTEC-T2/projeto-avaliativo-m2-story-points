import re
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage
from src.state import AgentState

# Carrega variáveis do .env
load_dotenv()

# Configura o modelo (gpt-4o-mini é rápido, barato e excelente para raciocínio estruturado)
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.1,
    api_key=os.getenv("GROQ_API_KEY")
)


def validate_issue(state: AgentState) -> dict:
    """Nó 1: Verifica se a issue tem informações mínimas para estimativa"""
    desc = state["issue_description"].strip()

    # Validação rápida de tamanho
    if not desc or len(desc) < 20:
        return {"is_valid": False, "missing_info": "A descrição está vazia ou muito curta. Adicione contexto técnico e funcional."}

    # LLM verifica se há objetivo, contexto e critérios
    prompt = f"""Analise se esta issue contém informações suficientes para estimar esforço técnico:
    DESCRIÇÃO: "{desc}"
    
    Critérios mínimos:
    1. Objetivo claro do que precisa ser feito
    2. Contexto técnico ou dependências mencionadas
    3. Critérios de aceitação ou detalhes funcionais
    
    Responda EXATAMENTE neste formato:
    VALIDO: SIM ou NAO
    FALTA: [liste o que falta ou escreva 'NADA']"""

    resp = llm.invoke([SystemMessage(content="Seja direto e objetivo."),
                      HumanMessage(content=prompt)]).content.strip()

    is_valid = "SIM" in resp.upper()
    missing = resp.split("FALTA:")[-1].strip() if not is_valid else None

    return {"is_valid": is_valid, "missing_info": missing}


def analyze_technical(state: AgentState) -> dict:
    """Nó 2: Decomposição, complexidade e riscos"""
    desc = state["issue_description"]

    prompt = f"""Como Engenheiro de Software Sênior, analise a issue abaixo:
    ISSUE: "{desc}"
    
    Forneça:
    1. ETAPAS: Lista de tarefas técnicas necessárias (separadas por ; )
    2. COMPLEXIDADE: BAIXA, MEDIA ou ALTA
    3. RISCOS: Principais riscos técnicos ou de negócio (separados por ; )
    
    Mantenha o formato exato:
    ETAPAS: ...
    COMPLEXIDADE: ...
    RISCOS: ..."""

    resp = llm.invoke([HumanMessage(content=prompt)]).content

    # Parsing robusto: case-insensitive, ignora formatação Markdown
    try:
        resp_clean = re.sub(r'\*+', '', resp)  # remove negrito do Markdown

        steps_match = re.search(
            r'ETAPAS\s*:\s*(.*?)(?=COMPLEXIDADE\s*:)', resp_clean, re.IGNORECASE | re.DOTALL)
        comp_match = re.search(
            r'COMPLEXIDADE\s*:\s*(.*?)(?=RISCOS\s*:)',  resp_clean, re.IGNORECASE | re.DOTALL)
        risks_match = re.search(r'RISCOS\s*:\s*(.*)',
                                resp_clean, re.IGNORECASE | re.DOTALL)

        steps = [s.strip() for s in steps_match.group(1).split(
            ";") if s.strip()] if steps_match else ["Análise não estruturada"]
        comp_str = comp_match.group(1).strip().split(
            "\n")[0] if comp_match else "MEDIA"
        risks = [r.strip() for r in risks_match.group(1).replace("\n", ";").split(
            ";") if r.strip()] if risks_match else ["Falha no parsing da resposta"]
    except Exception:
        steps, comp_str, risks = ["Análise não estruturada"], "MEDIA", [
            "Falha no parsing da resposta"]

    return {
        "identified_steps": steps,
        "complexity_level": comp_str,
        "risks": risks
    }


def estimate_points(state: AgentState) -> dict:
    """Nó 3: Cálculo dos Story Points + Justificativa final"""
    steps = state["identified_steps"]
    comp = state["complexity_level"]
    risks = state["risks"]

    # Prompt focado apenas no número
    points_prompt = f"""Com base na análise técnica:
    - Etapas: {len(steps)}
    - Complexidade: {comp}
    - Riscos: {len(risks)}
    
    Aplique a escala Fibonacci de esforço: 1, 2, 3, 5, 8, 13
    Regras rápidas:
    1-2: Simples, sem riscos, poucas etapas
    3-5: Média complexidade, integração interna
    8: Complexa, riscos moderados, dependência externa
    13: Alta incerteza, refatoração ou múltiplas integrações
    
    Responda APENAS com o NÚMERO."""

    resp_points = llm.invoke(
        [HumanMessage(content=points_prompt)]).content.strip()

    # Extrai apenas um número válido da escala Fibonacci do texto
    match = re.search(r'\b(13|8|5|3|2|1)\b', resp_points)
    points = int(match.group(1)) if match else 5

    # Gera justificativa textual
    just_prompt = f"""Escreva uma justificativa técnica concisa (máx. 4 linhas) para a estimativa de {points} Story Points.
    Mencione: complexidade ({comp}), volume de etapas e riscos principais."""

    justification = llm.invoke([HumanMessage(content=just_prompt)]).content

    return {"story_points": points, "final_justification": justification}
