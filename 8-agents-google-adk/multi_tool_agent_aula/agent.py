# Bibliotecas necessárias para lidar com data, hora e fuso horário, além da classe Agent da Google ADK
import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather(city: str) -> dict:
    """Retrieves the current weather report for a specified city.

    Args:
        city (str): The name of the city for which to retrieve the weather report.

    Returns:
        dict: status and result or error msg.
    """
    # Verificar se a cidade é new york e retornar um relatório de clima simulado
    if city.lower() == "new york":
        return {
            # mensagem de sucesso e relatório de clima simulado
            "status": "success",
            "report": (
                "The weather in New York is sunny with a temperature of 25 degrees"
                " Celsius (77 degrees Fahrenheit)."
            ),
        }
    else:
        return {
            # mensagem de erro para cidades que não são new york
            "status": "error",
            "error_message": f"Weather information for '{city}' is not available.",
        }


def get_current_time(city: str) -> dict:
    """Returns the current time in a specified city.

    Args:
        city (str): The name of the city for which to retrieve the current time.

    Returns:
        dict: status and result or error msg.
    """
    # Verificar se a cidade é new york e retornar a hora atual
    if city.lower() == "new york":
        tz_identifier = "America/New_York"
    else:
        return {
            # mensagem de erro para cidades que não são new york
            "status": "error",
            "error_message": (
                f"Sorry, I don't have timezone information for {city}."
            ),
        }

    # Obter a hora atual usando a biblioteca zoneinfo para lidar com fusos horários
    tz = ZoneInfo(tz_identifier)
    # Obter a hora atual no fuso horário especificado
    now = datetime.datetime.now(tz)
    # Formatar a hora atual em uma string legível
    report = (
        f'The current time in {city} is {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    # Retornar a hora atual formatada como parte do relatório de sucesso
    return {"status": "success", "report": report}

# Configuração do agente com nome, modelo, descrição, instrução e ferramentas
root_agent = Agent(
    # Nome do agente
    name="weather_time_agent",
    # Modelo de linguagem a ser utilizado pelo agente
    model="gemini-2.5-flash",
    # Descrição do agente
    description=(
        "Agent to answer questions about the time and weather in a city."
    ),
    # Instrução para o agente sobre seu comportamento e propósito
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    # Lista de ferramentas que o agente pode usar para obter informações
    tools=[get_weather, get_current_time],
)