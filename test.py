from api.api_huggingface import API

api = API()

PARAMETERS = {
    "max_new_tokens": 100,
    "temperature": 0.5
}

QUERY = "Can you please let us know more details about yourself"

query = {
    "inputs": QUERY, 
    "parameters": PARAMETERS
}

MODEL_OPTIONS = ["llama", "gpt2", "gemma"]

for model in MODEL_OPTIONS:
    print(f"Model: {model}")
    
    print("Retrieving response...")
    response = api.query(payload=query, model=model)
    print("Response:")
    print(response)
    print("\n")