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
            "role": "user",
            "content": "Explain the importance of fast language models",
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
        result = self.execute()
        self.messages.append({"role": "assistant", "content": result})
        return result
    
    # Método para executar a solicitação de chat utilizando o cliente Groq e retornar a resposta gerada pelo modelo.
    def execute(self):
        completion = client.chat.completions.create(
            messages= self.messages,
            model="llama-3.3-70b-versatile",
        )
        return completion.choices[0].message.content

# Definição de uma mensagem de sistema para configurar o comportamento do agente, descrevendo o loop de Thought, Action, PAUSE, Observation e as ações disponíveis para o agente.        
system_prompt = """
You run in a loop of Thought, Action, PAUSE, Observation.
At the end of the loop you output an Answer
Use Thought to describe your thoughts about the question you have been asked.
Use Action to run one of the actions available to you - then return PAUSE.
Observation will be the result of running those actions.

Your available actions are:

calculate:
e.g. calculate: 4 * 7 / 3
Runs a calculation and returns the number - uses Python so be sure to use floating point syntax if necessary

get_planet_mass:
e.g. get_planet_mass: Earth
returns weight of the planet in kg

Example session:

Question: What is the mass of Earth times 2?
Thought: I need to find the mass of Earth
Action: get_planet_mass: Earth
PAUSE 

You will be called again with this:

Observation: 5.972e24

Thought: I need to multiply this by 2
Action: calculate: 5.972e24 * 2
PAUSE

You will be called again with this: 

Observation: 1,1944×10e25

If you have the answer, output it as the Answer.

Answer: The mass of Earth times 2 is 1,1944×10e25.

Now it's your turn:
""".strip() 

# Criação de uma instância do agente utilizando o cliente Groq e a mensagem de sistema definida anteriormente.
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
result = neil_tyson("What is the mass of Earth times 5?")
print(result)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
neil_tyson.messages

# Exemplo de uso do agente para processar uma nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
result = neil_tyson()
print(result)

# Exemplo de uso da função get_planet_mass para obter a massa da Terra e imprimir o resultado.
obervation = get_planet_mass("Earth")
print(obervation)

# Exemplo de uso do obersation para criar um novo prompt para o agente, mostrando a observação obtida e preparando o próximo passo da interação.
next_prompt = f"Observation: {obervation}"
print(next_prompt)

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"obervation: {obervation}"
result = neil_tyson(next_prompt)
print(result)

# Imprime as mensagens trocadas entre o agente e o modelo de linguagem, mostrando o processo de pensamento, ações realizadas e observações feitas durante a interação.
neil_tyson.messages

# Exemplo de uso do agente para processar uma nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
result = neil_tyson()
print(result)

# Exemplo de uso da função calculate para realizar uma operação matemática e imprimir o resultado.
obervation = calculate("3.285e23 * 5")
print(obervation)

# Exemplo de uso do agente para processar a nova mensagem contendo a observação obtida, permitindo que o agente continue o processo de pensamento e ação com base na nova informação.
next_prompt = f"obervation: {obervation}"
result = neil_tyson(next_prompt)
print(result)

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
        result = agent(next_prompt)
        print(result)
        # Verifica se o agente pediu pausa e indicou uma ação a executar
        if "PAUSE" in result and "Action" in result:
            # Extrai o nome da ferramenta e o argumento da linha de ação
            action = re.findall(r"Action: ([a-z_]+): (.*)", result, re.IGNORECASE)
            chosen_tool = action[0][0]
            arg = action[0][1]
            # Se a ferramenta existir na lista permitida, executa e retorna observação
            if chosen_tool in tools:
                result_tool = eval(f"{chosen_tool}('{arg}')")
                next_prompt = f"Observation: {result_tool}"
            else:
                # Caso a ferramenta não exista, informa erro ao agente
                next_prompt = "Observation: Tool not found"
            
            # Imprime o próximo prompt que será enviado ao agente na próxima iteração
            print(next_prompt)
            continue
        # Verifica se o agente forneceu uma resposta final (Answer) e, se sim, encerra o loop
        if "Answer:" in result:
            break

# Chama a função de loop do agente com um número máximo de iterações, o prompt de sistema definido e uma pergunta inicial sobre a massa da Terra multiplicada por 5.
agent_loop(max_iterations=10, system=system_prompt, query="What is the mass of Earth plus the mass of Mercury and all of that times 5?")