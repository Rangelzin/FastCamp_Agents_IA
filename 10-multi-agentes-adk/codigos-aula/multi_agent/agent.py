# Bibliotecas necessárias para o agente, ferramenta do google search e biblioteca para obter a data e hora atual.
from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from .sub_agents.funny_nerd.agent import funny_nerd
from .sub_agents.news_analyst.agent import news_analyst
from .sub_agents.stock_analyst.agent import stock_analyst
from .tools.tools import get_current_time

# Definição do agente, utilizando a ferramenta de google search e a função para obter a data e hora atual.
root_agent = Agent(
    name="manager", # Nome do agente
    model="gemini-2.5-flash-lite", # Modelo utilizado para o agente
    description="Manager agent", # Descrição do agente
    instruction=""" 
        You are a manager agent that is responsible for overseeing the work of the other agents.

        Always delegate the task to the appropriate agent. Use your best judgement to determine which agent to delegate to.

        You are responsible for delegating tasks to the following agent:
        - stock_analyst
        - funny_nerd

        You also have access to the following tools:
        - news_analyst
        - get_current_time,
    """, # Instrução para o agente, explicando suas responsabilidades e as ferramentas que ele tem acesso.
    sub_agents=[stock_analyst, funny_nerd], # Sub-agentes que o agente pode delegar tarefas.
    tools=[ # Ferramentas que o agente pode utilizar.
        AgentTool(news_analyst), 
        get_current_time,
    ],
)