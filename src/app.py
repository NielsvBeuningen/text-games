# Load the general libraries
import streamlit as st
import os
import time
from collections import OrderedDict

# Set page title
st.set_page_config(
    page_title="Text Games",
)

# Define progress bar for setup
setup_text = "Setting up the environment..."
setup_bar = st.progress(0, text = setup_text)

setup_bar.progress(10, text = f"{setup_text} - Loading the configuration file")

### Load the configuration file
import yaml
from yaml.loader import SafeLoader
with open('./app_config.yaml') as file:
    st.session_state["config"] = yaml.load(file, Loader=SafeLoader)

setup_bar.progress(30, text = f"{setup_text} - Loading the API module")

### Loading the API module
from api.api_huggingface import API_huggingface
if "api" not in st.session_state:
    st.session_state.api = API_huggingface(
        base_parameters=st.session_state.config["HUGGINGFACE"]["BASE_PARAMS"],
        model_urls=st.session_state.config["HUGGINGFACE"]["MODEL_URLS"],
        api_key=st.session_state.config["HUGGINGFACE"]["API_KEY"]
        )

setup_bar.progress(50, text = f"{setup_text} - Loading the available agents")

### Load the agent modules
if "available_agents" not in st.session_state:
    st.session_state.available_agents = {}

    # Llama1B Agent
    from agents.llama import Llama1BAgent
    st.session_state.available_agents["llama1b"] = Llama1BAgent(api=st.session_state.api)

    # GPT2 Agent
    from agents.gpt2 import GPT2Agent
    st.session_state.available_agents["gpt2"] = GPT2Agent(api=st.session_state.api)



setup_bar.progress(70, text = f"{setup_text} - Loading the environment module")

### Load the environment modules
from env.jericho.env import JerichoEnv
if "game_env" not in st.session_state:
    st.session_state.game_name = "Zork1"
    st.session_state.game_env = JerichoEnv(f"./env/jericho/games/zork1.z5", seed=1, step_limit=100, get_valid=True)
    st.session_state.initial_observation, st.session_state.info = st.session_state.game_env.reset()


# Create placeholders in session state
if "game_agent" not in st.session_state:
    st.session_state.game_agent = st.session_state.available_agents["llama1b"]
    
if "agent_name" not in st.session_state:
    st.session_state.agent_name = "llama1b"

if "game_history" not in st.session_state:
    st.session_state.game_history = [st.session_state.config["HUGGINGFACE"]["BASE_PROMPT"]]
    
if "display_history" not in st.session_state:
    st.session_state.display_history = []

setup_bar.progress(100, text = f"{setup_text} - Loading the environment module")
setup_bar.empty()

api_exp = st.sidebar.expander("API Configuration", expanded=True)
with api_exp:
    selected_temperature = st.number_input("Temperature", value=0.5, min_value=0.0, max_value=1.0)
    selected_tokens = st.number_input("Max Tokens", value=100, min_value=1, max_value=1000)
    
    if st.button("Update API Configuration"):
        parameters = {
            "temperature": selected_temperature,
            "max_new_tokens": selected_tokens
        }
        st.session_state.api = API_huggingface(
            base_parameters=parameters,
            model_urls=st.session_state.config["HUGGINGFACE"]["MODEL_URLS"],
            api_key=st.session_state.config["HUGGINGFACE"]["API_KEY"]
            )
        st.session_state.available_agents["llama1b"] = Llama1BAgent(api=st.session_state.api)
        st.session_state.available_agents["gpt2"] = GPT2Agent(api=st.session_state.api)
        st.rerun()

agent_exp = st.sidebar.expander("Agent Configuration", expanded=True)
with agent_exp:
    selected_agent = st.selectbox("Select an agent", st.session_state.available_agents.keys())
    
    if st.button("Load Agent"):
        agent_setup_bar = st.progress(0, text = "Loading the agent...")
        st.session_state.game_history = [st.session_state.config["HUGGINGFACE"]["BASE_PROMPT"]]
        st.session_state.display_history = []
        agent_setup_bar.progress(10, text = "Loading the agent")
        st.session_state.game_agent = st.session_state.available_agents[selected_agent]
        st.session_state.agent_name = selected_agent
        agent_setup_bar.progress(100, text = "Loading the agent")
        agent_setup_bar.empty()
        st.rerun()

game_exp = st.sidebar.expander("Game Configuration", expanded=True)
with game_exp:
    selected_game_engine = st.selectbox("Select a game engine", ["Jericho"])
    if selected_game_engine == "Jericho":
        # Get the available games from the "env/games" directory
        available_games = os.listdir("./env/jericho/games")
        default_index = available_games.index("zork1.z5")
        selected_game = st.selectbox("Select a game", available_games, index = default_index)
        selected_seed = st.number_input("Seed", value=1, min_value=1, max_value=1000)
        selected_step_limit = st.number_input("Step Limit", value=100, min_value=1, max_value=10000)


        if st.button("Load Game"):
            game_setup_bar = st.progress(0, text = "Setting up the game environment...")
            game_setup_bar.progress(10, text = "Loading the game environment")
            st.session_state.game_history = [st.session_state.config["HUGGINGFACE"]["BASE_PROMPT"]]
            st.session_state.display_history = []
            st.session_state.game_name = selected_game.replace(".z[0-9]", "")
            game_setup_bar.progress(30, text = "Loading the game environment")
            st.session_state.game_env = JerichoEnv(f"./env/jericho/games/{selected_game}", seed=selected_seed, step_limit=selected_step_limit, get_valid=True)
            game_setup_bar.progress(70, text = "Loading the game environment")
            st.session_state.initial_observation, st.session_state.info = st.session_state.game_env.reset()
            game_setup_bar.progress(100, text = "Loading the game environment")
            game_setup_bar.empty()
            # initial_observation = initial_observation.replace("Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.\nZORK is a registered trademark of Infocom, Inc.\nRevision 88 / Serial number 840726\n\nWest of House\n", "").strip()
            st.rerun()
    else:
        st.error("Invalid game engine selected.")
        st.stop()

if st.session_state.game_agent is None:
    st.info("Please select an agent to continue.")
    st.stop()
    
if st.session_state.game_env is None:
    st.info("Please select a game to continue.")
    st.stop()
    
st.title(f"Game: {st.session_state.game_name}")
st.header(f"Agent: {st.session_state.agent_name}")

game_scores = st.empty()
final_scores = st.empty()

if st.button("Start Game"):    
    game_progress = st.empty()
        
    try:
        action, st.session_state.game_history, st.session_state.display_history = st.session_state.game_agent.generate_action(
            game_history=st.session_state.game_history, 
            display_history=st.session_state.display_history,
            observation=st.session_state.initial_observation, 
            info=st.session_state.info
            )
        
        progress_container = game_progress.container()
        event_expanders = {}
        # Reverse loop over display history to show events in order
        for i, event in enumerate(list(reversed(st.session_state.display_history))):
            event_expanders[i] = progress_container.expander(f"{event["event"]}")
            if event["role"] == "assistant":
                event_expanders[i].write(f"Valid actions: {event["valid_actions"]}")
            else:
                event_expanders[i].write(f"Full response: {event["full_response"]}")
                
            
        # game_progress.markdown("\n".join(reversed(st.session_state.display_history)))
        
    except Exception as e:
            st.error(f"Initial Error: {e}")
            st.stop()
            
    time.sleep(3)
            
    done = False
    while not done:
        # The resulting text-observation, reward, and game-over indicator is returned.
        observation, reward, done, info = st.session_state.game_env.step(action)
        
        # Total score and move-count are returned in the info dictionary
        game_scores.info(f'Total Score {info['score']} - Moves {info['moves']}')
        
        try:
            action, st.session_state.game_history, st.session_state.display_history = st.session_state.game_agent.generate_action(
                game_history=st.session_state.game_history, 
                display_history=st.session_state.display_history,
                observation=observation, 
                info=st.session_state.info
                )
            
            if action is None:
                done = True
                break
                                    
        except Exception as e:
            st.error(f"Error: {e}")
            done = True    
            
        progress_container = game_progress.container()
        event_expanders = {}
        # Reverse loop over display history to show events in order
        for i, event in enumerate(list(reversed(st.session_state.display_history))):
            event_expanders[i] = progress_container.expander(f"{event["event"]}")
            if event["role"] == "assistant":
                event_expanders[i].write(f"Valid actions: {event["valid_actions"]}")
            else:
                event_expanders[i].write(f"Full response: {event["full_response"]}")
        time.sleep(3)
        
    game_scores.success(f"Scored: {info['score']} out of {st.session_state.game_env.max_score}")
    final_scores.success(f"End scores: {st.session_state.game_env.end_scores}")