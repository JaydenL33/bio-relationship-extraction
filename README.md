# bio-relationship-extraction
Using RAG pipelines, and agentic AI, alongside prompt engineering to build out a Graph Database that allows us to search and visualise the relationships between organisms on pubmed. For my undergraduate thesis @ UTS
# How to use the App:
- Install Pyenv here [https://github.com/pyenv/pyenv?tab=readme-ov-file]
- Require version of Python is 3.11
- Poetry is required to be installed 
- HuggingFace Account and request access to Llama 3.2
- huggingface-cli login
- python run_llama.py
- Have Docker Installed 
- docker-compose up
- I am running this on a backwell gpu, so you may need to change the Pytorch version you are using
- This is design for WSL.
- Find out if you have NVIDIA GPU and CUDA version - nvidia-smi
- This could also be done on a M2 Mac using Llama 3B, but will require some changes.
- docker run --gpus all --ipc=host -it -v $(pwd):/workspace nvcr.io/nvidia/pytorch:25.02-py3
