import inspect
from trl import SFTTrainer, SFTConfig

print("--- SFTConfig init signature ---")
for k, v in inspect.signature(SFTConfig.__init__).parameters.items():
    if v.default is not inspect.Parameter.empty:
        print(f"  {k}: default={v.default}")
    else:
        print(f"  {k} (required)")

print("\n--- SFTTrainer init signature ---")
for k, v in inspect.signature(SFTTrainer.__init__).parameters.items():
    if v.default is not inspect.Parameter.empty:
        print(f"  {k}: default={v.default}")
    else:
        print(f"  {k} (required)")
