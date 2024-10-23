import re

class Llama1BAgent:
    def __init__(self, api=None):
        self.api = api
        self.model = "llama1b"

    def generate_action(self, game_history: list, display_history: list, observation: str, info: dict):
        
        event_info = f"""
        Game Master: {observation} Valid actions are: {info['valid']}.\n 
        What action would you like to take? Only state the action you would like to take, nothing more. \n 
        You: 
        """
        game_history.append(event_info)
        
        display_history.append({
            "role": "assistant", 
            "event": f"Game Master: {observation}", 
            "valid_actions": f"{info['valid']}"
            })
        
        query_input = " ".join(game_history)
                             
        payload = {
            "inputs": query_input
        }
        
        api_response = self.api.query(payload=payload, model=self.model)
        
        try:
            # Get the action by extracting it from the original query, since the model only returns the action
            action = api_response[0].get("generated_text")
            
            action = action.replace(query_input, "").strip()
        
            valid_actions = info['valid']
            
            # Extract the action from the generated text using the valid actions
            actions = re.findall(r'|'.join(valid_actions), action)
            
            if not action:
                action = "wait"
            else:      
                # If multiple actions are returned, take the first one
                action = actions[0]
            
        except:
            action = "wait"
            
        game_history.append(f"{action}\n")      
        display_history.append({
            "role": "user", 
            "event": f"Player: {action}",
            "full_response": f"{api_response}"
            })  
                        
        return action, game_history, display_history