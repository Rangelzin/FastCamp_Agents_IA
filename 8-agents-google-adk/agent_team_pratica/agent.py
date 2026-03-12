import os
import asyncio
from typing import Dict
from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from dotenv import load_dotenv

# 1. Setup Silencioso
load_dotenv(override=True)
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"
logging = __import__("logging")
logging.basicConfig(level=logging.ERROR)

MODEL1 = "groq/llama-3.3-70b-versatile"
MODEL2 = "gemma-3-27b-it"

# 2. Ferramentas (Retornando Dict sempre)
def generate_makefile(project_name: str, language: str = "C") -> Dict:
    """Gera um Makefile básico para projetos em C ou Go."""
    print(f"\n[⚙️ Tool] Gerando Makefile para {project_name} ({language})")
    if language.upper() == "GO":
        content = f"build:\n\tgo build -o {project_name} .\nrun:\n\t./{project_name}\nclean:\n\trm -f {project_name}"
    else:
        content = f"CC=gcc\nCFLAGS=-Wall -Wextra -O2\n\n{project_name}: main.c\n\t$(CC) $(CFLAGS) -o {project_name} main.c\n\nclean:\n\trm -f {project_name}"
    
    return {"status": "success", "makefile": content}

def format_commit(message: str) -> Dict:
    """Formata uma mensagem suja para o padrão Conventional Commits."""
    print(f"\n[⚙️ Tool] Formatando commit...")
    return {"status": "success", "commit": f"feat: {message.lower().strip()}"}

# 3. Definição Minimalista da Equipe
git_agent = Agent(
    name="git_agent",
    model=MODEL1,
    instruction="CRITICAL INSTRUCTION: Chame 'format_commit' UMA VEZ. Exiba a string gerada e PARE IMEDIATAMENTE.",
    tools=[format_commit]
)

tech_lead = Agent(
    name="tech_lead",
    model=MODEL2,
    instruction="Você é um Tech Lead focado em C e Go. Delegue formatação de mensagens para 'git_agent'. Use 'generate_makefile' quando pedirem scripts de build. Vá direto ao ponto.",
    tools=[generate_makefile],
    sub_agents=[git_agent]
)

# 4. Loop de Execução Interativa (CLI)
async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(app_name="dev_app", user_id="user_dev", session_id="session_1")
    runner = Runner(agent=tech_lead, app_name="dev_app", session_service=session_service)

    print("\n" + "="*50)
    print("🚀 CLI Dev Assistant Iniciado (Digite 'sair' para fechar)")
    print("="*50)

    while True:
        query = input("\n> ")
        if query.lower() in ['sair', 'exit', 'quit']:
            break
            
        content = types.Content(role='user', parts=[types.Part(text=query)])
        
        async for event in runner.run_async(user_id="user_dev", session_id="session_1", new_message=content):
            if event.is_final_response() and event.content:
                print(f"\n🤖 {event.content.parts[0].text}")
                break

if __name__ == "__main__":
    asyncio.run(main())