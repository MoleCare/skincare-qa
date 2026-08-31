import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finetune.huggingface_store import write_card
from finetune.models import HF_USER, SPECS


class HuggingFaceStoreTest(unittest.TestCase):
    def test_repos_live_under_yauhenbichel(self) -> None:
        self.assertEqual(HF_USER, "YauhenBichel")
        self.assertEqual(SPECS["skincare-qa"].hf_repo, "YauhenBichel/skincare-qa-1b")

    def test_write_card(self) -> None:
        spec = SPECS["skincare-qa"]
        dest = Path(__file__).resolve().parents[1] / "data" / "_card_test"
        readme = write_card(spec, dest)
        text = readme.read_text(encoding="utf-8")
        self.assertIn("Not a medical device", text)
        self.assertIn("YauhenBichel/skincare-qa-1b", text)


if __name__ == "__main__":
    unittest.main()
