---
license: apache-2.0
base_model: Qwen/Qwen2.5-Coder-0.5B-Instruct
library_name: mlx
tags:
  - mlx
  - lora
  - qwen2.5-coder
  - python
language:
  - en
---

# python-vibe-0.5b

LoRA-fused **Qwen2.5-Coder-0.5B-Instruct** (4-bit MLX) for short Python “vibe coding”
answers. Owned by [YauhenBichel](https://huggingface.co/YauhenBichel).

Serve it behind `PythonVibeGuard` (empty / leaked keys / `curl|sh`). The guard
is not this repo — it lives in the training workbench.

## Use

```python
from mlx_lm import load, generate

model, tokenizer = load("YauhenBichel/python-vibe-0.5b")
```

Or pull the folder and point Ollama / llama.cpp at a GGUF if one is attached.

Base weights: `Qwen/Qwen2.5-Coder-0.5B-Instruct` (Apache-2.0).
