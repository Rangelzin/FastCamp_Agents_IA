import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent

def get_weather_planet(planet: str) -> dict:
    """Obtém o relatório meteorológico para um planeta especificado.

    Args:
        planet (str): O nome do planeta para o qual obter as informações meteorológicas.

    Returns:
        dict: status e resultado ou mensagem de erro.
    """
    dados_mockados = {
    "mercurio": {
        "status": "sucesso",
        "report": (
            "O tempo em Mercúrio é extremamente quente durante o dia, com temperaturas que podem chegar a 430 graus Celsius (800 graus Fahrenheit), e extremamente frio durante a noite, com temperaturas que podem cair para -180 graus Celsius (-290 graus Fahrenheit)."
        ),
    },
    "venus": {
        "status": "sucesso",
        "report": (
            "O tempo em Vênus é extremamente quente e hostil, com temperaturas médias de cerca de 465 graus Celsius (870 graus Fahrenheit) devido a um efeito estufa descontrolado. A atmosfera é composta principalmente por dióxido de carbono, com nuvens de ácido sulfúrico, tornando as condições inóspitas para a vida como conhecemos."
        ),
    },
    "terra": {
        "status": "sucesso",
        "report": (
            "O tempo na Terra varia amplamente dependendo da localização e da estação do ano, mas geralmente é temperado com uma variedade de condições climáticas, incluindo chuva, sol, neve e vento."
        ),
    },
    "marte": {
        "status": "sucesso",
        "report": (
            "O tempo em Marte é frio e seco, com temperaturas médias de cerca de -80 graus Celsius (-112 graus Fahrenheit). A atmosfera é fina e composta principalmente por dióxido de carbono, com ventos que podem criar tempestades de poeira massivas."
        ),
    },
    "jupiter": {
        "status": "sucesso",
        "report": (
            "O tempo em Júpiter é caracterizado por ventos fortes e tempestades, incluindo a Grande Mancha Vermelha, uma tempestade anticiclônica que tem durado por séculos. A atmosfera é composta principalmente por hidrogênio e hélio, com temperaturas que variam de -145 graus Celsius (-234 graus Fahrenheit) na parte superior a cerca de 24.000 graus Celsius (43.000 graus Fahrenheit) no interior."
        ),
    },
    "urano": {
        "status": "sucesso",
        "report": (
            "O tempo em Urano é frio e ventoso, com temperaturas médias de cerca de     -224 graus Celsius (-371 graus Fahrenheit). A atmosfera é composta principalmente por hidrogênio, hélio e metano, com ventos que podem atingir velocidades de até 900 km/h (560 mph)." 
        ),
    },
    "netuno": {
        "status": "sucesso",
        "report": (
            "O tempo em Netuno é frio e ventoso, com temperaturas médias de cerca de -214 graus Celsius (-353 graus Fahrenheit). A atmosfera é composta principalmente por hidrogênio, hélio e metano, com ventos que podem atingir velocidades de até 2.100 km/h (1.300 mph), tornando Netuno o planeta mais ventoso do sistema solar."
        ),
    },
}
    
    match (planet.lower()):
        case 'mercurio':
            return {
                "status": dados_mockados["mercurio"]["status"],
                "report": dados_mockados["mercurio"]["report"],
            }
        case 'venus':
            return {
                "status": dados_mockados["venus"]["status"],
                "report": dados_mockados["venus"]["report"],
            }
        case 'terra':
            return {
                "status": dados_mockados["terra"]["status"],
                "report": dados_mockados["terra"]["report"],
            }
        case 'marte':
            return {
                "status": dados_mockados["marte"]["status"],
                "report": dados_mockados["marte"]["report"],
            }
        case 'jupiter':
            return {
                "status": dados_mockados["jupiter"]["status"],
                "report": dados_mockados["jupiter"]["report"],
            }
        case 'saturno':
            return {
                "status": dados_mockados["saturno"]["status"],
                "report": dados_mockados["saturno"]["report"],
            }
        case 'urano':
            return {
                "status": dados_mockados["urano"]["status"],
                "report": dados_mockados["urano"]["report"],
            }
        case 'netuno':
            return {
                "status": dados_mockados["netuno"]["status"],
                "report": dados_mockados["netuno"]["report"],
            }
        case _ :
            return {
            "status": "erro",
            "error_message": f"Informações meteorológicas para '{planet}' não estão disponíveis.",
        }


def get_current_time(city: str) -> dict:
    """Retorna a hora atual em uma cidade especificada.

    Args:
        city (str): O nome da cidade para a qual obter a hora atual.

    Returns:
        dict: status e resultado ou mensagem de erro.
    """

    if city.lower() == "sao paulo":
        tz_identifier = "America/Sao_Paulo"
    else:
        return {
            "status": "erro",
            "error_message": (
                f"Desculpe, não tenho informação do horário em {city}."
            ),
        }

    tz = ZoneInfo(tz_identifier)
    now = datetime.datetime.now(tz)
    report = (
        f'A hora atual em {city} é {now.strftime("%Y-%m-%d %H:%M:%S %Z%z")}'
    )
    return {"status": "sucesso", "report": report}

root_agent = Agent(
    name="agente_clima_hora",
    model="gemini-2.5-flash",
    description=(
        "Agente para responder perguntas sobre a hora de uma cidade e informações meteorológicas de um planeta do sistema solar."
    ),
    instruction=(
        "Você é um agente prestativo que pode responder perguntas do usuário sobre a hora atual em uma cidade e informações meteorológicas de um planeta do sistema solar. Use as ferramentas disponíveis para obter as informações necessárias e forneça respostas claras e precisas ao usuário."
    ),
    tools=[get_weather_planet, get_current_time],
)