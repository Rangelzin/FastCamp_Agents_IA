# Bibliotecas necessárias para o agente, ferramenta do google search e biblioteca para obter a data e hora atual.
from google.adk.agents import Agent
from google.adk.tools import google_search
from datetime import datetime

# Tool para pegar a data e hora atual
def get_current_time() -> dict:
    """
    Get the current time in the format "YYYY-MM-DD HH:MM:SS".
    """
    # Retorna a data e hora atual formatada como string
    return {
        "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# Definição do agente, utilizando a ferramenta de google search e a função para obter a data e hora atual.
root_agent = Agent(
    name="tool_agent", # Nome do agente
    model="gemini-2.5-flash-lite", # Modelo utilizado para o agente
    description="Tool agent", # Descrição do agente
    instruction="""
    You are a helpful assistant that can use the following tools:
    - get_current_time
    """, # Instrução para o agente, informando que ele é um assistente útil que pode usar a ferramenta de google search.
    #tools=[google_search] 
    tools=[get_current_time]
)
