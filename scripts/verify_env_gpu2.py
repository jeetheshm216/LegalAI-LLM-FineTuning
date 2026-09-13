import torch
import transformers
import datasets
import accelerate
import peft
import trl

print("torch:", torch.__version__)
print("transformers:", transformers.__version__)
print("datasets:", datasets.__version__)
print("accelerate:", accelerate.__version__)
print("peft:", peft.__version__)
print("trl:", trl.__version__)

print("CUDA available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Visible GPU count:", torch.cuda.device_count())
    print("Visible GPU 0:", torch.cuda.get_device_name(0))
