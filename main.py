import os
from dotenv import load_dotenv
from src.graph import graph


def main():
    load_dotenv()

    # 1. Validação de segurança da chave
    if not os.getenv("GROQ_API_KEY"):
        print("❌ Erro: GROQ_API_KEY não encontrada no arquivo .env")
        print(
            "💡 Crie um arquivo .env na raiz do projeto com: GROQ_API_KEY=sua_chave_aqui")
        return

    print("🚀 Agente de Story Points - Iniciando...\n")

    # 2. Issue de exemplo para teste
    test_issue = """
    Título: Implementar sistema de login com OAuth2 (Google)
    Descrição: 
    - Criar tela de login com botão 'Entrar com Google'
    - Configurar credenciais no Google Cloud Console
    - Implementar fluxo OAuth2 no backend (Python/FastAPI)
    - Salvar token de acesso e refresh token no banco de dados (PostgreSQL)
    - Criar middleware de autenticação para proteger rotas privadas
    - Adicionar testes unitários e de integração
    """

    print("📥 Issue recebida:")
    print(test_issue.strip())
    print("\n⏳ Processando...")

    try:
        # 3. Executa o grafo LangGraph
        result = graph.invoke({"issue_description": test_issue})

        print("\n✅ Processamento concluído!")
        print("-" * 50)

        # 4. Exibe os dados extraídos do State
        print(f" Story Points: {result.get('story_points', 'N/A')}")
        print(f" Complexidade: {result.get('complexity_level', 'N/A')}")
        print(f"️ Riscos: {', '.join(result.get('risks', []))}")
        print(
            f"📝 Etapas: {len(result.get('identified_steps', []))} identificadas")
        print(f"💬 Justificativa:\n{result.get('final_justification', 'N/A')}")

        # Feedback caso a issue seja rejeitada
        if not result.get('is_valid', True):
            print(f"\n Issue rejeitada: {result.get('missing_info', '')}")

    except Exception as e:
        print(f"\n❌ Erro na execução: {e}")


if __name__ == "__main__":
    main()
