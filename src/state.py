from typing import TypedDict, List, Optional

# Definimos a estrutura de dados que vai "viajar" pelo nosso grafo


class AgentState(TypedDict):
    # 1. Entrada: A descrição da Issue que o usuário quer estimar
    issue_description: str

    # 2. Validação: O agente precisa decidir se a issue tem info suficiente
    is_valid: bool
    missing_info: Optional[str]  # Se faltar info, guarda o que falta aqui

    # 3. Análise Técnica (o agente vai preenchendo isso)
    # Lista de etapas necessárias (ex: "Criar banco", "Fazer API")
    identified_steps: List[str]
    complexity_level: str       # "Baixa", "Média", "Alta"
    risks: List[str]            # Riscos identificados

    # 4. Saída Final: O resultado para o usuário
    story_points: int           # A estimativa final (1, 2, 3, 5, 8...)
    final_justification: str    # O texto explicando o porquê da estimativa
