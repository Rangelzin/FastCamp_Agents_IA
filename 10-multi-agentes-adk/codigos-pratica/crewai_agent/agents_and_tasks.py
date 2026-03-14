# agents_and_tasks.py
import os
from crewai_tools import SerperDevTool
from crewai import Agent, Task, LLM
from dotenv import load_dotenv

load_dotenv(override=True)

llm = LLM(
    model="gemini/gemini-2.5-flash",
    api_key=os.getenv("GOOGLE_API_KEY")
)

search_tool = SerperDevTool()

# Agente 1 - Pesquisador Planetário
researcher = Agent(
    llm=llm,
    role="Pesquisador Planetário",
    goal="Buscar a gravidade superficial do planeta {planeta} em m/s²",
    backstory="""Você é um astrônomo especialista em física planetária. 
    Você pesquisa e fornece dados precisos sobre a gravidade dos planetas.""",
    tools=[search_tool],
    verbose=True
)

# Agente 2 - Calculador de Força Peso
calculator = Agent(
    llm=llm,
    role="Calculador de Força Peso",
    goal="Calcular a força peso de uma pessoa com massa {massa}kg no planeta {planeta} e comparar com a Terra",
    backstory="""Você é um físico especialista em mecânica clássica.
    Você recebe dados de gravidade e calcula a força peso, gerando relatórios comparativos.""",
    verbose=True
)

# Tarefa 1 - Pesquisa
research_task = Task(
    description="""Pesquise a gravidade superficial do planeta {planeta} em m/s².
    Retorne também massa do planeta, distância do Sol e uma curiosidade.""",
    expected_output="Gravidade em m/s², massa, distância do Sol e uma curiosidade sobre o planeta.",
    agent=researcher
)

# Tarefa 2 - Cálculo
calculation_task = Task(
    description="""Com a gravidade encontrada, calcule a força peso de uma pessoa 
    com massa {massa}kg usando P = m * g.
    Compare com o peso na Terra (g = 9.8 m/s²) e mostre quanto a pessoa pesaria 
    em todos os planetas do sistema solar.""",
    expected_output="Relatório com força peso no planeta, comparação com a Terra e tabela com todos os planetas.",
    agent=calculator,
    context=[research_task]
)