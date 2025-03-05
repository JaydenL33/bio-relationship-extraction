import torch
print(torch.__version__)
print(torch.cuda.is_available())  # Should return True
print(torch.version.cuda)  # Should match your CUDA version