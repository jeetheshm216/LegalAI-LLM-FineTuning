import torch

print("CUDA:", torch.cuda.is_available())
print("GPU count:", torch.cuda.device_count())

for i in range(torch.cuda.device_count()):
    p = torch.cuda.get_device_properties(i)
    print(
        f"GPU {i}: {p.name}, "
        f"VRAM={p.total_memory / 1024**3:.2f} GB"
    )
