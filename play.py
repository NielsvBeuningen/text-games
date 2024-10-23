# Loading the API module
print("Loading API module...")
from src.api.api_huggingface import API_huggingface

import time
import re

api = API_huggingface()

PARAMETERS = {
    "max_new_tokens": 10,
    "temperature": 0.1
}

MODEL_OPTIONS = [
    "llama", 
    "gpt2",
    "gemma"
    ]

def generate_action(game_history, observation, info):

    game_history.append(f"Game Master: {observation} Valid actions are: {info['valid']}.\n What action would you like to take? Only state the action you would like to take, nothing more. \n Player: ")

    query_input = " ".join(game_history)
            
    print(f"{query_input}")
            
    payload = {
        "inputs": query_input, 
        "parameters": PARAMETERS
    }
    
    action = api.query(payload=payload, model=model)
    
    try:
        # Get the action by extracting it from the original query, since the model only returns the action
        action = action[0].get("generated_text")
    except:
        print(f"Error: {action}")
        wait = input("Would you like to continue? (y/n): ")
        if wait.lower() == "n":
            return None, game_history
        else:
            return "wait", game_history
    
    action = action.replace(query_input, "").strip()
    
    valid_actions = info['valid']
    
    # Extract the action from the generated text using the valid actions
    actions = re.findall(r'|'.join(valid_actions), action)
    
    if not action:
        print(f"Invalid action: {action}")
        wait = input("Would you like to continue? (y/n): ")
        if wait.lower() == "n":
            action = None
        else:
            action = "wait"
            
    # If multiple actions are returned, take the first one
    action = actions[0]
        
    game_history.append(f"{action}\n")
    
    print(f"Action: {action}\n")
    
    time.sleep(20)
        
    return action, game_history
                                
    

for model in MODEL_OPTIONS:
    print("Model: ", model)
    print("-" * 80)
    
    game_history = []
    
    # Import the JerichoEnv class from the drrn.env module
    print("Loading JerichoEnv environment...")
    from drrn.env import JerichoEnv
    from jericho import *

    game = "zork1.z5"
    print("Loading game: ", game)

    # Create the environment, optionally specifying a random seed
    env = JerichoEnv(f"games/{game}", seed=1, step_limit=100, get_valid=True)
    initial_observation, info = env.reset()

    # Remove game-specific information from the initial observation
    # initial_observation = initial_observation.replace("Copyright (c) 1981, 1982, 1983 Infocom, Inc. All rights reserved.\nZORK is a registered trademark of Infocom, Inc.\nRevision 88 / Serial number 840726\n\nWest of House\n", "").strip()
    
    try:
        action, game_history = generate_action(game_history=game_history, observation=initial_observation, info=info)
    except Exception as e:
            print(f"Error: {e}")
            print("=" * 50)
            continue
    
    
    done = False
    while not done:
        # The resulting text-observation, reward, and game-over indicator is returned.
        observation, reward, done, info = env.step(action)
        # Total score and move-count are returned in the info dictionary
        print('Total Score', info['score'], 'Moves', info['moves'])
        
        
        try:
            action, game_history = generate_action(game_history=game_history, observation=observation, info=info)
            
            if action is None:
                done = True
                break
                                    
        except Exception as e:
            print(f"Error: {e}")
            done = True        
        
    print(f"Scored: {info['score']} out of {env.max_score}")
    print(f"End scores: {env.end_scores}")


    print("=" * 80)