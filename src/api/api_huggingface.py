import requests
import streamlit as st

class API_huggingface:
    def __init__(self, base_parameters: dict = None, model_urls: dict = None, api_key: str = None):
        self.base_url = "https://api-inference.huggingface.co/models/"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.base_parameters = base_parameters
        self.model_urls = model_urls


    def query(self, payload: dict, model: str) -> dict:
        payload["parameters"] = self.base_parameters
        
        api_url = self.base_url + self.model_urls[model]
        
        response = requests.post(api_url, headers=self.headers, json=payload)
        return response.json()
    
    