import torch
print('CUDA is available:', torch.cuda.is_available())
print('Device count:', torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    name = torch.cuda.get_device_name(i)
    mem = torch.cuda.get_device_properties(i).total_memory / (1024**3)
    free = torch.cuda.mem_get_info(i)[0] / (1024**3)
    print(f'GPU {i}: {name} - Total: {mem:.2f} GB, Free: {free:.2f} GB')
