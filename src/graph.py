from langgraph.graph import StateGraph, START, END
from src.state import AgentState
from src.nodes import validate_issue, analyze_technical, estimate_points
import os

# 🔧 FERRAMENTA OBRIGATÓRIA: Escrita de relatório técnico


def save_report_tool(state: AgentState) -> dict:
    """Ferramenta que gera um arquivo .md com a estimativa final"""
    os.makedirs("results", exist_ok=True)
    safe_id = hash(state["issue_description"]) % 10000
    filename = f"results/estimativa_{safe_id}.md"

    content = f"""# 📊 Estimativa de Story Points
**Descrição:** {state['issue_description'][:100]}...
**Pontos Estimados:** {state['story_points']}
**Complexidade:** {state['complexity_level']}
**Etapas:** {', '.join(state['identified_steps'])}
**Riscos:** {', '.join(state['risks'])}
**Justificativa:** {state['final_justification']}
"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    # Atualiza o estado confirmando a ação da ferramenta
    return {"final_justification": state["final_justification"] + f"\n\n✅ Relatório salvo em: {filename}"}

# 🧭 Roteamento condicional (validação da issue)


def route_validation(state: AgentState):
    if not state.get("is_valid", False):
        return "rejeitada"
    return "aprovada"


# 🏗️ Montagem do Grafo
workflow = StateGraph(AgentState)

# 1. Registrar os nós
workflow.add_node("validar", validate_issue)
workflow.add_node("analisar", analyze_technical)
workflow.add_node("estimar", estimate_points)
workflow.add_node("salvar_relatorio", save_report_tool)

# 2. Definir as conexões
workflow.add_edge(START, "validar")

workflow.add_conditional_edges(
    "validar",
    route_validation,
    {
        "rejeitada": END,   # Se inválida, encerra e devolve o erro
        "aprovada": "analisar"  # Se válida, segue para análise técnica
    }
)

workflow.add_edge("analisar", "estimar")
workflow.add_edge("estimar", "salvar_relatorio")
workflow.add_edge("salvar_relatorio", END)

# 3. Compilar o grafo (pronto para execução)
graph = workflow.compile()
