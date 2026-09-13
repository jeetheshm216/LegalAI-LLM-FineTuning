#!/usr/bin/env python3
import inspect
import sys
import torch
import transformers
import datasets
import accelerate
import peft
import trl
import bitsandbytes
from trl import SFTTrainer, SFTConfig

print("Python executable:", sys.executable)
print("Python version:   ", sys.version.split()[0])
print("PyTorch:          ", torch.__version__)
print("Transformers:     ", transformers.__version__)
print("Datasets:         ", datasets.__version__)
print("Accelerate:       ", accelerate.__version__)
print("PEFT:             ", peft.__version__)
print("TRL:              ", trl.__version__)
print("bitsandbytes:     ", bitsandbytes.__version__)

print("\n--- CUDA & GPU Status ---")
print("CUDA Available:   ", torch.cuda.is_available())
print("Device Count:     ", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(f"GPU {i}:           {torch.cuda.get_device_name(i)}")

print("\n--- TRL SFTTrainer / SFTConfig API Inspection ---")
print("SFTTrainer class: ", SFTTrainer)
print("SFTConfig class:  ", SFTConfig)

sig_trainer = inspect.signature(SFTTrainer.__init__)
print("SFTTrainer accepts 'args':            ", "args" in sig_trainer.parameters)
print("SFTTrainer accepts 'peft_config':     ", "peft_config" in sig_trainer.parameters)
print("SFTTrainer accepts 'processing_class':", "processing_class" in sig_trainer.parameters)
print("SFTTrainer accepts 'tokenizer':       ", "tokenizer" in sig_trainer.parameters)

sig_config = inspect.signature(SFTConfig.__init__)
print("SFTConfig accepts 'max_seq_length':   ", "max_seq_length" in sig_config.parameters)
print("SFTConfig accepts 'dataset_text_field':", "dataset_text_field" in sig_config.parameters)
print("SFTConfig subclasses TrainingArguments:", issubclass(SFTConfig, transformers.TrainingArguments))

print("\nAll training imports and API checks SUCCESSFUL without model download.")
