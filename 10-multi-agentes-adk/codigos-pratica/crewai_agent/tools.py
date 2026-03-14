# tools.py
# SerperDevTool já cuida da busca
# Mas se quiser uma tool customizada de cálculo:
from crewai.tools import BaseTool

class PesoCalculatorTool(BaseTool):
    name: str = "Calculadora de Força Peso"
    description: str = "Calcula a força peso dado massa em kg e gravidade em m/s²"

    def _run(self, massa: float, gravidade: float) -> str:
        peso = massa * gravidade
        peso_terra = massa * 9.8
        proporcao = peso / peso_terra
        return f"Força Peso: {peso:.2f} N | Na Terra seria {peso_terra:.2f} N | Proporção: {proporcao:.2f}x"
