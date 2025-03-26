import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Model ID from Hugging Face
model_id = "meta-llama/Llama-3.2-3B-Instruct"

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.bfloat16,  # Use bfloat16 for efficiency
    device_map="auto"  # Automatically map to available GPU/CPU
)

# Prepare the input prompt
messages = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hello! Can you tell me what Llama 3.2 is?"}
]

# Apply chat template and tokenize
input_text = tokenizer.apply_chat_template(messages, tokenize=False)
inputs = tokenizer(input_text, return_tensors="pt").to(model.device)

# Generate response
outputs = model.generate(
    **inputs,
    max_new_tokens=200,
    do_sample=True,
    temperature=0.7,
    top_p=0.9
)

# Decode and print the response
response = tokenizer.decode(outputs[0], skip_special_tokens=True)
print("Assistant:", response[len(input_text):].strip())