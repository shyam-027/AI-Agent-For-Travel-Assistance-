# model_helper.py
import os
from google.adk.models.lite_llm import LiteLlm

def get_model():
    model_name = os.environ.get("MODEL_OVERRIDE", "groq/llama-3.3-70b-versatile")
    
    if model_name.startswith("together/"):
        together_key = os.environ.get("TOGETHER_API_KEY")
        if together_key:
            print(f"✅ Using Together.ai model: {model_name}")
            return LiteLlm(
                model=model_name,
                api_key=together_key,
                temperature=0.1,
                max_tokens=2048,
                parallel_tool_calls=False,
            )
    
    # ... rest of your existing code