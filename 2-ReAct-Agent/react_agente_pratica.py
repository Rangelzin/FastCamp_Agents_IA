# Bibliotecas para manipular variáveis de ambiente, e manipulação de arquivos e diretórios e para interagir com a API Groq.
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv() # Carrega as variáveis do arquivo .env para o os.environ

# Criação do cliente Groq utilizando a chave da API armazenada na variável de ambiente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# Criação de uma solicitação de conclusão de chat utilizando o modelo "llama-3.3-70b-versatile" e uma mensagem do usuário.
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explique a importância de modelos de linguagem rápidos",
        }
    ],
    # Especificação do modelo a ser utilizado para a geração da resposta.
    model="llama-3.3-70b-versatile",
)

# Impressão do conteúdo da resposta gerada pelo modelo.
print(chat_completion.choices[0].message.content)

# Definição de uma classe Agent para implementação de um agente que pode interagir com o modelo de linguagem para realizar tarefas específicas.
class Agent:
    # funcão de inicialização da classe Agent, que recebe um cliente Groq e uma mensagem de sistema opcional para configurar o comportamento do agente.
    def __init__(self, client, system):
        self.client = client
        self.system = system
        self.messages = []
        if self.system is not None:
            self.messages.append({"role": "system", "content": self.system})
    # Método para processar uma mensagem do usuário, adicionar a mensagem à lista de mensagens, executar a solicitação de chat e retornar a resposta gerada pelo modelo.
    def __call__(self, message=""):
        if message:
            self.messages.append({"role": "user", "content": message})
        resultado = self.executar()
        self.messages.append({"role": "assistant", "content": resultado})
        return resultado
    
    # Método para executar a solicitação de chat utilizando o cliente Groq e retornar a resposta gerada pelo modelo.
    def executar(self):
        completion = client.chat.completions.create(
            messages= self.messages,
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content


# Definição de um prompt de sistema para o agente, que orienta o comportamento do agente em um loop de pensamento, ação, pausa e observação, e define as ações disponíveis para o agente executar com base nas perguntas recebidas.       
system_prompt = """
Você executa em um loop de Pensamento, Ação, PAUSA, Observação.
Ao final do loop você produz uma Resposta
Use Pensamento para descrever seus pensamentos sobre a pergunta que você recebeu.
Use Ação para executar uma das ações disponíveis para você - depois retorne PAUSA.
Observação será o resultado da execução dessas ações.

Suas ações disponíveis são:

calcular_funcao_2ograu:
ex. calcular_funcao_2ograu: a , b, c
Executa a fórmula de Bhaskara para resolver uma equação quadrática com os coeficientes a, b e c fornecidos e retorna o resultado

calcular_tempo_luz:
ex. calcular_tempo_luz: Mars, Earth
Calcula o tempo que a luz leva para viajar entre a origem (padrão: Earth) e o planeta informado, retornando tempo em segundos e minutos e a distância aproximada.

Sessão de exemplo:

Pergunta: Quanto tempo a luz leva para viajar de Marte até a Terra?
Pensamento: Preciso calcular o tempo que a luz leva para viajar entre Marte e a Terra usando a ação disponível
Ação: calcular_tempo_luz: Mars, Earth
PAUSA

Você será chamado novamente com isso:

Observação: tempo = 187.4, distancia = 5.62e10

Se tiver a resposta, produza-a como a Resposta.

Resposta: A luz leva aproximadamente 187.4 segundos (ou cerca de 3.12 minutos) para viajar de Marte até a Terra, cobrindo uma distância aproximada de 5.62 × 10^10 km.

Agora é sua vez:
""".strip()

import math

# Função para calcular as raízes de uma equação do 2º grau (ax² + bx + c = 0).
# Aceita:
# - três argumentos numéricos (a, b, c), ou
# - uma string no formato "a, b, c".
def calcular_funcao_2ograu(a, b=None, c=None):
    # Suporta chamada com string única no formato "a, b, c"
    if isinstance(a, str) and b is None and c is None:
        partes = [p.strip() for p in a.split(",")]

        # Valida formato esperado
        if len(partes) != 3:
            return {"erro": "Use o formato: a, b, c"}

        # Converte valores para float
        a, b, c = map(float, partes)
    else:
        # Suporta chamada tradicional com 3 argumentos
        a, b, c = float(a), float(b), float(c)

    # Em equação de 2º grau, 'a' não pode ser zero
    if a == 0:
        return {"erro": "Coeficiente 'a' deve ser diferente de 0"}

    # Calcula discriminante (delta)
    delta = b**2 - 4 * a * c

    # Retorna raízes conforme o valor de delta
    if delta > 0:
        # Duas raízes reais distintas
        x1 = (-b + math.sqrt(delta)) / (2 * a)
        x2 = (-b - math.sqrt(delta)) / (2 * a)
        return {"delta": delta, "x1": x1, "x2": x2}
    elif delta == 0:
        # Uma raiz real (raiz dupla)
        x = -b / (2 * a)
        return {"delta": delta, "x": x}
    else:
        # Duas raízes complexas conjugadas
        real = -b / (2 * a)
        imag = math.sqrt(-delta) / (2 * a)
        return {"delta": delta, "x1": complex(real, imag), "x2": complex(real, -imag)}


# Função para calcular o tempo que a luz leva entre dois planetas.
# Aceita:
# - dois argumentos: destino, origem (origem padrão = "Earth"), ou
# - uma string única: "destino, origem".
def calcular_tempo_luz(destino, origem="Earth"):
    # Permite chamada com string única: "destino, origem"
    if isinstance(destino, str) and "," in destino and origem == "Earth":
        partes = [p.strip() for p in destino.split(",")]
        if len(partes) == 2:
            destino, origem = partes[0], partes[1]

    # Distância média ao Sol em quilômetros (aproximações)
    distancia_sol_km = {
        "mercury": 57_900_000,
        "venus": 108_200_000,
        "earth": 149_600_000,
        "mars": 227_900_000,
        "jupiter": 778_500_000,
        "saturn": 1_433_000_000,
        "uranus": 2_877_000_000,
        "neptune": 4_503_000_000,
    }

    d = distancia_sol_km.get(destino.lower())
    o = distancia_sol_km.get(origem.lower())

    if d is None or o is None:
        return {"erro": "Planeta inválido. Use nomes como Earth, Mars, Jupiter, etc."}

    # Distância aproximada entre órbitas (modelo simplificado)
    distancia_km = abs(d - o)

    # Velocidade da luz em km/s
    c_km_s = 299_792.458

    # Tempo em segundos e minutos
    tempo_s = distancia_km / c_km_s

    return {
        "tempo": round(tempo_s, 2),
        "distancia": distancia_km,
    }

        
# Criação de uma instância do agente utilizando o cliente Groq e a mensagem de sistema definida anteriormente.
agent = Agent(client, system_prompt)

# Exemplo de uso do agente para responder a uma pergunta sobre a massa da Terra multiplicada por 5, utilizando as ações definidas para obter a massa do planeta e realizar o cálculo necessário.
resultado = agent("Quanto tempo a luz leva para viajar de Mercúrio até a Terra?")
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
agent.messages

# Exemplo de uso da função get_planet_mass para obter a massa da Terra e imprimir o resultadoado.
obervation = calcular_tempo_luz("Earth","Mercury")
print(obervation)

# Exemplo de uso do obersation para criar um novo prompt para o agente, mostrando a observação obtida e preparando o próximo passo da interação.
next_prompt = f"Observação: {obervation}"
print(next_prompt)

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"Observação: {obervation}"
resultado = agent(next_prompt)
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
agent.messages

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"Observação: {obervation}"
resultado = agent(next_prompt)
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
agent.messages

import re

# Função para implementar o loop do agente, onde o agente processa uma mensagem de entrada, executa ações com base nas mensagens geradas e continua o processo até atingir um número máximo de iterações ou obter uma resposta final.
def agent_loop(iteracoes_max, system, query):
    # Cria uma instância nova do agente com o prompt de sistema
    agent = Agent(client, system)

    # Mapa de ferramentas permitidas (nome -> função)
    tools = {
        "calcular_tempo_luz": calcular_tempo_luz,
        "calcular_funcao_2ograu": calcular_funcao_2ograu,
    }

    # Primeiro prompt enviado ao agente
    next_prompt = query
    # Contador para evitar loop infinito
    i = 0

    # Executa até atingir o limite de iterações
    while i < iteracoes_max:
        i += 1

        # Envia o prompt atual e recebe resposta do modelo
        resultado = agent(next_prompt)
        print(resultado)

        # Só tenta executar tool se o modelo indicou PAUSA + Ação
        # Regex aceita "Ação" e "Acao", com variação de caixa
        if "PAUSA" in resultado.upper() and re.search(r"A[cç][aã]o:", resultado, re.IGNORECASE):
            # Extrai: nome da ferramenta + argumentos
            # Exemplo esperado: "Ação: calcular_tempo_luz: Mars, Earth"
            match = re.search(r"A[cç][aã]o:\s*([a-z0-9_]+)\s*:\s*(.*)", resultado, re.IGNORECASE)

            # Se o formato não bater, devolve observação para o agente corrigir
            if not match:
                next_prompt = "Observação: Não consegui interpretar a ação. Use formato: Ação: nome_tool: argumentos"
                print(next_prompt)
                continue

            # Nome da tool e string de argumentos extraídos da resposta
            chosen_tool = match.group(1).strip()
            arg = match.group(2).strip()

            # Busca a função correspondente no dicionário
            tool_fn = tools.get(chosen_tool)
            if not tool_fn:
                # Tool inexistente: avisa o agente via observação
                next_prompt = f"Observação: Ferramenta '{chosen_tool}' não encontrada"
                print(next_prompt)
                continue

            try:
                # Executa a tool mantendo contrato atual (1 string de entrada)
                resultado_tool = tool_fn(arg)
                # Retorna resultado da tool como observação para próxima iteração
                next_prompt = f"Observação: {resultado_tool}"
            except Exception as e:
                # Captura falhas de execução e devolve erro ao agente
                next_prompt = f"Observação: erro ao executar '{chosen_tool}': {e}"

            print(next_prompt)
            continue

        # Encerra o loop quando o modelo já trouxe resposta final
        if "Resposta:" in resultado:
            break

# Chama a função de loop do agente com um número máximo de iterações, o prompt de sistema definido e uma pergunta inicial sobre o tempo para luz chegar em Netuno.
agent_loop(iteracoes_max=10, system=system_prompt, query="Quanto tempo a luz leva para viajar de Vênus até a Netuno?")

# Chama a função de loop do agente com um número máximo de iterações, o prompt de sistema definido e uma pergunta inicial sobre a soma de raizes de uma equação do 2º grau.
agent_loop(iteracoes_max=10, system=system_prompt, query="Quero que você some as raizes da equação x^2 + 3x – 4 = 0")