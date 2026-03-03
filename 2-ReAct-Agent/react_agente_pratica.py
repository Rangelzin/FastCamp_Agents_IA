# Biblioteca para manipular variáveis de ambiente, e manipulação de arquivos e diretórios

from dotenv import load_dotenv
import os
from groq import Groq

load_dotenv()

# Criação do cliente Groq utilizando a chave da API armazenada na variável de ambiente
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))


# Criação de uma solicitação de conclusão de chat utilizando o modelo "llama-3.3-70b-versatile" e uma mensagem do usuário.
chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "Usuario",
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
            self.messages.append({"role": "Usuário", "content": message})
        resultado = self.executar()
        self.messages.append({"role": "Agente", "content": resultado})
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
No final do loop você fornece uma Resposta
Use Pensamento para descrever seus pensamentos sobre a pergunta que lhe foi feita.
Use Ação para executar uma das ações disponíveis para você - depois retorne PAUSA.
Observação será o resultadoado da execução dessas ações.

Suas ações disponíveis são:

[nome_ação]
e.g. obter_massa_planeta: [nome_planeta] - Retorna a massa do planeta especificado
e.g. calcular: [operação matemática] - Retorna o resultadoado da operação matemática
Descrição da ação

Sessão de exemplo:

Pergunta: Qual é a massa da Terra multiplicada por 2?
Pensamento: Preciso encontrar a massa da Terra
Ação: obter_massa_planeta: Terra
PAUSA

Você será chamado novamente com isto:

Observação: 5.972e24

Pensamento: Preciso multiplicar isto por 2
Ação: calcular: 5.972e24 * 2
PAUSA

Você será chamado novamente com isto: 

Observação: 1,1944×10e25

Se você tiver a resposta, forneça-a como Resposta.

Resposta: A massa da Terra multiplicada por 2 é 1,1944×10e25.

Agora é sua vez:
Pergunta: Qual é a massa da Terra multiplicada por 2?
""".strip()

# Função para realizar o calculo de uma operação matemática utilizando a função eval, permitindo que o agente execute cálculos dinâmicos com base nas ações solicitadas.
def calculate(operation):
    return eval(operation)

# Função para obter a massa de um planeta específico, utilizando uma estrutura de correspondência (match-case) para retornar a massa correta com base no nome do planeta fornecido.
def get_planet_mass(planet) -> float: 
    match planet.lower():
        case "earth":
            return 5.972e24
        case "jupiter":
            return 1.898e27
        case "mars":
            return 6.39e23
        case "mercury":
            return 3.285e23
        case "neptune":
            return 1.024e26
        case "saturn":
            return 5.683e26
        case "uranus":
            return 8.681e25
        case "venus":
            return 4.867e24
        case _:
            return 0.0
        
# Criação de uma instância do agente utilizando o cliente Groq e a mensagem de sistema definida anteriormente.
neil_tyson = Agent(client, system_prompt)

# Exemplo de uso do agente para responder a uma pergunta sobre a massa da Terra multiplicada por 5, utilizando as ações definidas para obter a massa do planeta e realizar o cálculo necessário.
resultado = neil_tyson("What is the mass of Earth times 5?")
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
neil_tyson.messages

# Exemplo de uso do agente para processar uma nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
resultado = neil_tyson()
print(resultado)

# Exemplo de uso da função get_planet_mass para obter a massa da Terra e imprimir o resultadoado.
obervation = get_planet_mass("Earth")
print(obervation)

# Exemplo de uso do obersation para criar um novo prompt para o agente, mostrando a observação obtida e preparando o próximo passo da interação.
next_prompt = f"Observation: {obervation}"
print(next_prompt)

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"obervation: {obervation}"
resultado = neil_tyson(next_prompt)
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
neil_tyson.messages

# Exemplo de uso do agente para processar uma nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
resultado = neil_tyson()
print(resultado)

# Exemplo de uso da função calculate para realizar uma operação matemática e imprimir o resultadoado.
obervation = calculate("3.285e23 * 5")
print(obervation)

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"obervation: {obervation}"
resultado = neil_tyson(next_prompt)
print(resultado)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
neil_tyson.messages

import re

# Função para implementar o loop do agente, onde o agente processa uma mensagem de entrada, executa ações com base nas mensagens geradas e continua o processo até atingir um número máximo de iterações ou obter uma resposta final.
def agent_loop(max_iterations, system, query):
    # Cria uma nova instância do agente com o prompt de sistema definido
    agent = Agent(client, system_prompt)
    # Lista de ferramentas permitidas para execução dinâmica
    tools = ['calculate', 'get_planet_mass']
    # Primeiro prompt que será enviado ao agente (a pergunta inicial)
    next_prompt = query
    # Contador de iterações para evitar loop infinito
    i = 0

    # Executa o loop até atingir o limite máximo de iterações
    while i < max_iterations:
        i += 1
        # Envia o prompt atual ao agente e captura a resposta
        resultado = agent(next_prompt)
        print(resultado)
        # Verifica se o agente pediu pausa e indicou uma ação a executar
        if "PAUSE" in resultado and "Action" in resultado:
            # Extrai o nome da ferramenta e o argumento da linha de ação
            action = re.findall(r"Action: ([a-z_]+): (.*)", resultado, re.IGNORECASE)
            chosen_tool = action[0][0]
            arg = action[0][1]
            # Se a ferramenta existir na lista permitida, executa e retorna observação
            if chosen_tool in tools:
                resultado_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {resultado_tool}"
            else:
                # Caso a ferramenta não exista, informa erro ao agente
                next_prompt = "Observation: Tool not found"
            
            # Imprime o próximo prompt que será enviado ao agente na próxima iteração
            print(next_prompt)
            continue
        # Verifica se o agente forneceu uma resposta final (Answer) e, se sim, encerra o loop
        if "Answer:" in resultado:
            break

# Chama a função de loop do agente com um número máximo de iterações, o prompt de sistema definido e uma pergunta inicial sobre a massa da Terra multiplicada por 5.
agent_loop(max_iterations=10, system=system_prompt, query="What is the mass of Earth plus the mass of Mercury and all of that times 5?")