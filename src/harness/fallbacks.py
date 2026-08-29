"""Fixed replies when the guard blocks twice. Never invent a diagnosis or a secret."""

from finetune.systems import SKINCARE_DISCLAIMER

SKINCARE_FALLBACK = (
    "I can't tell you what this is — that needs someone to look at it. "
    "Book a GP or dermatologist if a mole is changing, bleeding, or worrying you. "
    f"{SKINCARE_DISCLAIMER}"
)

PYTHON_VIBE_FALLBACK = (
    "I can't ship that draft. Ask for a smaller local script "
    "(stdlib, no secrets, no curl|sh) and I will try again."
)
