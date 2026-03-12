# ============================================================================
# SEÇÃO 1: INSTALAÇÃO E IMPORTAÇÕES
# ============================================================================

import os
import asyncio
import logging
import warnings
from typing import Optional, Dict
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
from google.adk.tools.tool_context import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
logging.basicConfig(level=logging.ERROR)

print("Libraries imported.")

# ============================================================================
# SEÇÃO 2: CONFIGURAÇÃO E CONSTANTES GLOBAIS
# ============================================================================

load_dotenv(override=True)

google_key = os.environ.get('GOOGLE_API_KEY')
groq_key = os.environ.get('GROQ_API_KEY')

print("API Keys configuradas.")

os.environ['OPENAI_API_KEY'] = groq_key
os.environ['GOOGLE_API_KEY'] = google_key
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

MODEL_GEMMA3 = "gemma-3-27b-it"
MODEL_GPT_GROQ = "groq/llama-3.1-8b-instant"

APP_NAME = "weather_tutorial_app"
USER_ID = "user_1"
SESSION_ID = "session_001"
APP_NAME_GPT = "weather_tutorial_app_gpt"
USER_ID_GPT = "user_1_gpt"
SESSION_ID_GPT = "session_001_gpt"
APP_NAME_STATEFUL = "weather_tutorial_stateful"
USER_ID_STATEFUL = "user_state_demo"
SESSION_ID_STATEFUL = "session_state_demo_001"
APP_NAME_TEAM = "weather_tutorial_agent_team"
USER_ID_TEAM = "user_1_agent_team"
SESSION_ID_TEAM = "session_001_agent_team"

print("\nEnvironment configured.")

# ============================================================================
# SEÇÃO 3: DEFINIÇÃO DE FERRAMENTAS (TOOLS)
# ============================================================================

def get_weather(city: str) -> Dict:
    print(f"--- Tool: get_weather called for city: {city} ---")
    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"status": "success", "report": "The weather in New York is sunny with a temperature of 25°C."},
        "london": {"status": "success", "report": "It's cloudy in London with a temperature of 15°C."},
        "tokyo": {"status": "success", "report": "Tokyo is experiencing light rain and a temperature of 18°C."},
    }

    if city_normalized in mock_weather_db:
        return mock_weather_db[city_normalized]
    else:
        return {"status": "error", "error_message": f"Sorry, I don't have weather information for '{city}'."}


def say_hello(name: str = "") -> str:
    if name:
        greeting = f"Hello, {name}!"
        print(f"--- Tool: say_hello called with name: {name} ---")
    else:
        greeting = "Hello there!"
        print(f"--- Tool: say_hello called without a specific name ---")
    return greeting

def say_goodbye() -> str:
    print(f"--- Tool: say_goodbye called ---")
    return "Goodbye! Have a great day."

def get_weather_stateful(city: str, tool_context: ToolContext) -> Dict:
    print(f"--- Tool: get_weather_stateful called for {city} ---")
    preferred_unit = tool_context.state.get("user_preference_temperature_unit", "Celsius")
    print(f"--- Tool: Reading state 'user_preference_temperature_unit': {preferred_unit} ---")

    city_normalized = city.lower().replace(" ", "")

    mock_weather_db = {
        "newyork": {"temp_c": 25, "condition": "sunny"},
        "london": {"temp_c": 15, "condition": "cloudy"},
        "tokyo": {"temp_c": 18, "condition": "light rain"},
    }

    if city_normalized in mock_weather_db:
        data = mock_weather_db[city_normalized]
        temp_c = data["temp_c"]
        condition = data["condition"]

        if preferred_unit == "Fahrenheit":
            temp_value = (temp_c * 9/5) + 32
            temp_unit = "°F"
        else:
            temp_value = temp_c
            temp_unit = "°C"

        report = f"The weather in {city.capitalize()} is {condition} with a temperature of {temp_value:.0f}{temp_unit}."
        result = {"status": "success", "report": report}
        print(f"--- Tool: Generated report in {preferred_unit}. Result: {result} ---")

        tool_context.state["last_city_checked_stateful"] = city
        print(f"--- Tool: Updated state 'last_city_checked_stateful': {city} ---")

        return result
    else:
        error_msg = f"Sorry, I don't have weather information for '{city}'."
        print(f"--- Tool: City '{city}' not found. ---")
        return {"status": "error", "error_message": error_msg}


print("✅ All tools defined.")

# ============================================================================
# SEÇÃO 4: CALLBACKS E GUARDRAILS
# ============================================================================

def block_keyword_guardrail(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    agent_name = callback_context.agent_name
    print(f"--- Callback: block_keyword_guardrail running for agent: {agent_name} ---")

    last_user_message_text = ""
    if llm_request.contents:
        for content in reversed(llm_request.contents):
            if content.role == 'user' and content.parts:
                if content.parts[0].text:
                    last_user_message_text = content.parts[0].text
                    break

    print(f"--- Callback: Inspecting last user message: '{last_user_message_text[:100]}...' ---")

    keyword_to_block = "BLOCK"
    if keyword_to_block in last_user_message_text.upper():
        print(f"--- Callback: Found '{keyword_to_block}'. Blocking LLM call! ---")
        callback_context.state["guardrail_block_keyword_triggered"] = True

        return LlmResponse(
            content=types.Content(
                role="model",
                parts=[types.Part(text=f"I cannot process this request because it contains the blocked keyword '{keyword_to_block}'.")],
            )
        )
    else:
        print(f"--- Callback: Keyword not found. Allowing LLM call for {agent_name}. ---")
        return None

print("✅ Guardrails defined.")

# ============================================================================
# SEÇÃO 5: CRIAÇÃO DE AGENTES
# ============================================================================

def create_weather_agent(
    name: str = "weather_agent_v1",
    model: str = MODEL_GEMMA3,
    description: str = "Provides weather information for specific cities."
) -> Optional[Agent]:
    try:
        agent = Agent(
            name=name,
            model=model,
            description=description,
            instruction="You are a helpful weather assistant. "
                        "When the user asks for the weather in a specific city, "
                        "use the 'get_weather' tool to find the information. "
                        "If the tool returns an error, inform the user politely. "
                        "If the tool is successful, present the weather report clearly.",
            tools=[get_weather],
        )
        print(f"✅ Agent '{name}' created.")
        return agent
    except Exception as e:
        print(f"❌ Could not create agent '{name}'. Error: {e}")
        return None

def create_gpt_weather_agent(
    name: str = "weather_agent_gpt",
    model_name: str = MODEL_GPT_GROQ
) -> Optional[Agent]:
    try:
        agent = Agent(
            name=name,
            model=LiteLlm(model=model_name),
            description="Provides weather information (using GPT-OSS).",
            instruction="You are a helpful weather assistant powered by GPT-OSS. "
                        "Use the 'get_weather' tool for city weather requests. "
                        "Clearly present successful reports or polite error messages.",
            tools=[get_weather],
        )
        print(f"✅ Agent '{name}' created using model '{model_name}'.")
        return agent
    except Exception as e:
        print(f"❌ Could not create GPT agent. Error: {e}")
        return None

def create_greeting_agent(
    name: str = "greeting_agent",
    model_name: str = LiteLlm(model=MODEL_GPT_GROQ) # MODEL_GEMMA3
) -> Optional[Agent]:
    try:
        agent = Agent(
            model= model_name,
            name=name,
            instruction="You are the Greeting Agent. Your ONLY task is to provide a friendly greeting using the 'say_hello' tool. "
                        "Do not engage in any other conversation.",
            description="Handles simple greetings and hellos using the 'say_hello' tool.",
            tools=[say_hello],
        )
        print(f"✅ Agent '{name}' created.")
        return agent
    except Exception as e:
        print(f"❌ Could not create greeting agent. Error: {e}")
        return None

def create_farewell_agent(
    name: str = "farewell_agent",
    model_name: str = MODEL_GEMMA3
) -> Optional[Agent]:
    try:
        agent = Agent(
            model=model_name,
            name=name,
            instruction="You are the Farewell Agent. Your ONLY task is to provide a polite goodbye message using the 'say_goodbye' tool. "
                        "Do not perform any other actions.",
            description="Handles simple farewells using the 'say_goodbye' tool.",
            tools=[say_goodbye],
        )
        print(f"✅ Agent '{name}' created.")
        return agent
    except Exception as e:
        print(f"❌ Could not create farewell agent. Error: {e}")
        return None

def create_root_agent(
    name: str,
    model_name: str = MODEL_GEMMA3,
    greeting_agent: Optional[Agent] = None,
    farewell_agent: Optional[Agent] = None,
    tool_func=get_weather,
    output_key: Optional[str] = None,
    before_model_callback: Optional[callable] = None,
    description: str = "Main coordinator agent."
) -> Optional[Agent]:
    try:
        sub_agents = []
        if greeting_agent:
            sub_agents.append(greeting_agent)
        if farewell_agent:
            sub_agents.append(farewell_agent)

        agent = Agent(
            name=name,
            model=model_name,
            description=description,
            instruction="You are the main Weather Agent coordinating a team. "
                        "Use 'get_weather' for weather requests. "
                        "Delegate greetings to 'greeting_agent' and farewells to 'farewell_agent'.",
            tools=[tool_func],
            sub_agents=sub_agents if sub_agents else None,
        )
        
        if output_key:
            agent.output_key = output_key
        if before_model_callback:
            agent.before_model_callback = before_model_callback
            
        print(f"✅ Root Agent '{name}' created with {len(sub_agents)} sub-agents.")
        return agent
    except Exception as e:
        print(f"❌ Could not create root agent '{name}'. Error: {e}")
        return None

print("✅ Agent creation functions defined.")

# ============================================================================
# SEÇÃO 6: FUNÇÕES ASSINCRONIZADAS PARA INTERAÇÃO
# ============================================================================

async def call_agent_async(
    query: str,
    runner: Runner,
    user_id: str,
    session_id: str
) -> str:
    print(f"\n>>> User Query: {query}")

    content = types.Content(role='user', parts=[types.Part(text=query)])
    final_response_text = "Agent did not produce a final response."

    async for event in runner.run_async(user_id=user_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            if event.content and event.content.parts:
                final_response_text = event.content.parts[0].text
            elif event.actions and event.actions.escalate:
                final_response_text = f"Agent escalated: {event.error_message or 'No specific message.'}"
            break

    print(f"<<< Agent Response: {final_response_text}")
    return final_response_text

async def init_session(
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    state: Optional[Dict] = None
):
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=state
    )
    print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session

async def run_basic_conversation(
    runner: Runner,
    user_id: str,
    session_id: str,
    queries: list
):
    print("\n--- Testing Basic Conversation ---")
    for query in queries:
        await call_agent_async(query, runner, user_id, session_id)

async def run_team_conversation(
    runner: Runner,
    user_id: str,
    session_id: str,
):
    print("\n--- Testing Agent Team Delegation ---")
    
    queries = [
        "Hello there!",
        "What is the weather in New York?",
        "Thanks, bye!"
    ]
    
    for query in queries:
        await call_agent_async(query, runner, user_id, session_id)

async def run_stateful_conversation(
    runner: Runner,
    session_service: InMemorySessionService,
    user_id: str,
    session_id: str,
    app_name: str,
):
    print("\n--- Testing State: Temp Unit Conversion & output_key ---")

    print("--- Turn 1: Requesting weather in London (expect Celsius) ---")
    await call_agent_async(
        "What's the weather in London?",
        runner, user_id, session_id
    )

    print("\n--- Manually Updating State: Setting unit to Fahrenheit ---")
    try:
        stored_session = session_service.sessions[app_name][user_id][session_id]
        stored_session.state["user_preference_temperature_unit"] = "Fahrenheit"
        print(f"--- State updated. Current unit: {stored_session.state.get('user_preference_temperature_unit')} ---")
    except KeyError as e:
        print(f"--- Error updating state: {e} ---")

    print("\n--- Turn 2: Requesting weather in New York (expect Fahrenheit) ---")
    await call_agent_async(
        "Tell me the weather in New York.",
        runner, user_id, session_id
    )

    print("\n--- Turn 3: Sending a greeting ---")
    await call_agent_async("Hi!", runner, user_id, session_id)

async def run_guardrail_test_conversation(
    runner: Runner,
    user_id: str,
    session_id: str,
):
    print("\n--- Testing Model Input Guardrail ---")

    print("--- Turn 1: Requesting weather in London (expect allowed) ---")
    await call_agent_async("What is the weather in London?", runner, user_id, session_id)

    print("\n--- Turn 2: Requesting with blocked keyword (expect blocked) ---")
    await call_agent_async("BLOCK the request for weather in Tokyo", runner, user_id, session_id)

    print("\n--- Turn 3: Sending a greeting (expect allowed) ---")
    await call_agent_async("Hello again", runner, user_id, session_id)

async def inspect_final_state(
    session_service: InMemorySessionService,
    app_name: str,
    user_id: str,
    session_id: str,
    keys_to_inspect: list
):
    print("\n--- Inspecting Final Session State ---")
    try:
        final_session = await session_service.get_session(
            app_name=app_name,
            user_id=user_id,
            session_id=session_id
        )
        if final_session:
            for key in keys_to_inspect:
                value = final_session.state.get(key, "Not Set")
                print(f"{key}: {value}")
        else:
            print("❌ Error: Could not retrieve final session state.")
    except Exception as e:
        print(f"❌ Error inspecting state: {e}")

print("✅ Async functions defined.")

# ============================================================================
# SEÇÃO 7: EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTE 1: CONVERSA BÁSICA COM AGENTE GEMMA")
    print("="*80)
    
    try:
        weather_agent = create_weather_agent()
        session_service = InMemorySessionService()
        session = asyncio.run(init_session(session_service, APP_NAME, USER_ID, SESSION_ID))
        runner = Runner(agent=weather_agent, app_name=APP_NAME, session_service=session_service)
        
        asyncio.run(run_basic_conversation(
            runner,
            USER_ID,
            SESSION_ID,
            ["What is the weather like in London?"]
        ))
    except Exception as e:
        print(f"❌ Erro no Teste 1: {e}")

    print("\n" + "="*80)
    print("TESTE 2: AGENTE GPT")
    print("="*80)
    
    try:
        gpt_agent = create_gpt_weather_agent()
        session_service_gpt = InMemorySessionService()
        session_gpt = asyncio.run(init_session(session_service_gpt, APP_NAME_GPT, USER_ID_GPT, SESSION_ID_GPT))
        runner_gpt = Runner(agent=gpt_agent, app_name=APP_NAME_GPT, session_service=session_service_gpt)
        
        asyncio.run(run_basic_conversation(
            runner_gpt,
            USER_ID_GPT,
            SESSION_ID_GPT,
            ["What's the weather in Tokyo?"]
        ))
    except Exception as e:
        print(f"❌ Erro no Teste 2: {e}")

    print("\n" + "="*80)
    print("TESTE 3: TEAM COM SUB-AGENTES")
    print("="*80)
    
    try:
        greeting_agent = create_greeting_agent()
        farewell_agent = create_farewell_agent()
        team_agent = create_root_agent(
            "weather_agent_v2",
            greeting_agent=greeting_agent,
            farewell_agent=farewell_agent,
            description="Main coordinator with sub-agents"
        )
        
        if team_agent:
            session_service_team = InMemorySessionService()
            session_team = asyncio.run(init_session(session_service_team, APP_NAME_TEAM, USER_ID_TEAM, SESSION_ID_TEAM))
            runner_team = Runner(agent=team_agent, app_name=APP_NAME_TEAM, session_service=session_service_team)
            
            asyncio.run(run_team_conversation(runner_team, USER_ID_TEAM, SESSION_ID_TEAM))
    except Exception as e:
        print(f"❌ Erro no Teste 3: {e}")

    print("\n" + "="*80)
    print("TESTE 4: CONVERSA COM STATE (CELSIUS/FAHRENHEIT)")
    print("="*80)
    
    try:
        greeting_agent_state = create_greeting_agent()
        farewell_agent_state = create_farewell_agent()
        stateful_agent = create_root_agent(
            "weather_agent_v4_stateful",
            greeting_agent=greeting_agent_state,
            farewell_agent=farewell_agent_state,
            tool_func=get_weather_stateful,
            output_key="last_weather_report",
            description="Main agent with state-aware weather tool"
        )
        
        if stateful_agent:
            session_service_stateful = InMemorySessionService()
            initial_state = {"user_preference_temperature_unit": "Celsius"}
            session_stateful = asyncio.run(init_session(
                session_service_stateful,
                APP_NAME_STATEFUL,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL,
                initial_state
            ))
            runner_stateful = Runner(
                agent=stateful_agent,
                app_name=APP_NAME_STATEFUL,
                session_service=session_service_stateful
            )
            
            asyncio.run(run_stateful_conversation(
                runner_stateful,
                session_service_stateful,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL,
                APP_NAME_STATEFUL
            ))
            
            asyncio.run(inspect_final_state(
                session_service_stateful,
                APP_NAME_STATEFUL,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL,
                ["user_preference_temperature_unit", "last_weather_report", "last_city_checked_stateful"]
            ))
    except Exception as e:
        print(f"❌ Erro no Teste 4: {e}")

    print("\n" + "="*80)
    print("TESTE 5: MODEL INPUT GUARDRAIL")
    print("="*80)
    
    try:
        greeting_agent_guard = create_greeting_agent()
        farewell_agent_guard = create_farewell_agent()
        guardrail_agent = create_root_agent(
            "weather_agent_v5_guardrail",
            greeting_agent=greeting_agent_guard,
            farewell_agent=farewell_agent_guard,
            tool_func=get_weather_stateful,
            output_key="last_weather_report",
            before_model_callback=block_keyword_guardrail,
            description="Agent with keyword guardrail"
        )
        
        if guardrail_agent:
            session_service_guard = InMemorySessionService()
            initial_state = {"user_preference_temperature_unit": "Celsius"}
            session_guard = asyncio.run(init_session(
                session_service_guard,
                APP_NAME_STATEFUL,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL,
                initial_state
            ))
            runner_guard = Runner(
                agent=guardrail_agent,
                app_name=APP_NAME_STATEFUL,
                session_service=session_service_guard
            )
            
            asyncio.run(run_guardrail_test_conversation(
                runner_guard,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL
            ))
            
            asyncio.run(inspect_final_state(
                session_service_guard,
                APP_NAME_STATEFUL,
                USER_ID_STATEFUL,
                SESSION_ID_STATEFUL,
                ["guardrail_block_keyword_triggered", "last_weather_report"]
            ))
    except Exception as e:
        print(f"❌ Erro no Teste 5: {e}")

    print("\n" + "="*80)
    print("TODOS OS TESTES CONCLUÍDOS")
    print("="*80)