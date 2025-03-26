from fastapi import FastAPI
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# Load model and tokenizer at startup
model_name = "NousResearch/Llama-1b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name).to("cuda")

@app.get("/")
def read_root():
    return {"message": "LLM API is running!"}

@app.post("/generate/")
def generate_text(prompt: str):
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    output = model.generate(**inputs, max_length=50)
    return {"generated_text": tokenizer.decode(output[0], skip_special_tokens=True)}