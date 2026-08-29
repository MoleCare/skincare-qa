---
license: llama3.2
base_model: meta-llama/Llama-3.2-1B-Instruct
library_name: mlx
tags:
  - mlx
  - lora
  - llama
  - skin-health
  - not-a-medical-device
language:
  - en
---

# skincare-qa-1b

LoRA-fused **Llama-3.2-1B-Instruct** (4-bit MLX) for educational skin-health Q&A.
Owned by [YauhenBichel](https://huggingface.co/YauhenBichel).

**Not a medical device.** It must not diagnose a person's lesion. Serve only
behind MoleCare [skin-care-harness](https://github.com/MoleCare/skin-care-harness).
Training text comes from [molecare-mcp](https://github.com/MoleCare/molecare-mcp)
knowledge, not a parallel medical KB.

## Use

```python
from mlx_lm import load, generate

model, tokenizer = load("YauhenBichel/skincare-qa-1b")
```

Base weights: `meta-llama/Llama-3.2-1B-Instruct` (Llama 3.2 Community License).
You still need Meta's license grant to use Llama weights.
