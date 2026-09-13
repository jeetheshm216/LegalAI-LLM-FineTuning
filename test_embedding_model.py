import os
import torch
from sentence_transformers import SentenceTransformer

print("=== CHECKING EMBEDDING MODEL ON GPU 0 ===")
print("CUDA Available:", torch.cuda.is_available())
if torch.cuda.is_available():
    print("Device Name:", torch.cuda.get_device_name(0))
    print("VRAM Allocated (MB):", torch.cuda.memory_allocated(0) / 1024**2)

model_name = "BAAI/bge-large-en-v1.5"
print(f"Loading {model_name} onto cuda:0...")
device = "cuda:0" if torch.cuda.is_available() else "cpu"
model = SentenceTransformer(model_name, device=device)
dim = model.get_sentence_embedding_dimension()
max_len = model.max_seq_length

print("Model Loaded Successfully!")
print("Verified Embedding Dimension:", dim)
print("Max Sequence Length:", max_len)

sample_text = "Section 103 of Bharatiya Nyaya Sanhita, 2023: Punishment for murder"
vec = model.encode([sample_text])
print("Test Vector Shape:", vec.shape)
print("Vector Norm (Normalized):", float((vec**2).sum()))
