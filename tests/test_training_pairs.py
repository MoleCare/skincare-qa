"""Every training pair carries the disclaimer, and each question is asked once.

`_close()` appends `SKINCARE_DISCLAIMER` to an answer, and every pair in
the file is written to call it. Nothing required that. A pair added
without `_close()` would have shipped into the training data with no
disclaimer and no test would have said so, which on this subject is the
one thing that must not happen quietly.

The second check is about data quality rather than safety. Two answers
to the same question teach a model that both are right, and the weaker
one dilutes the stronger. One arrived that way: "Do people with darker
skin need to wear sunscreen?" alongside an existing "Do people with dark
skin need sunscreen?" whose answer carried a point the new one dropped —
that skin cancers on darker skin are often diagnosed later.
"""

import re
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from finetune.skincare_from_molecare import (  # noqa: E402
    pairs_diagnosis_boundary,
    pairs_everyday_skincare,
    pairs_from_resources,
)
from finetune.systems import SKINCARE_DISCLAIMER  # noqa: E402

# The pair sources that are written by hand. `pairs_from_kb` and
# `pairs_from_webapp` read files that are not in this repository.
BY_HAND = (
    ("everyday skincare", pairs_everyday_skincare),
    ("diagnosis boundary", pairs_diagnosis_boundary),
    ("resources", pairs_from_resources),
)


# Calibrated on the pairs below rather than chosen by feel. The one real
# duplicate scores 0.78; the closest legitimate pair, a baby-specific
# question beside a general one, scores 0.64 and gives different advice.
# 0.72 sits between them. It is a blunt instrument and the number is a
# judgement, so a pair it flags is a question to look at, not a verdict.
#
#   0.78  "Do people with dark skin need sunscreen?"
#         "Do people with darker skin need to wear sunscreen?"     duplicate
#   0.64  "How can I protect my baby from the sun?"
#         "How do I protect my skin from the sun?"                 distinct
#   0.50  "When should I see a doctor about my mole?"
#         "When should I see a dermatologist?"                      distinct
SAME_QUESTION = 0.72

# Crude, and deliberately so: `darker` and `dark` are the same word for
# this purpose, and nothing here needs a stemmer to know it.
_SUFFIXES = ("iest", "ing", "est", "ers", "er", "es", "s")


def _stems(text: str) -> set[str]:
    found = set()
    for word in re.findall(r"[a-z0-9]+", text.lower()):
        for suffix in _SUFFIXES:
            if len(word) > len(suffix) + 2 and word.endswith(suffix):
                word = word[: -len(suffix)]
                break
        found.add(word)
    return found


def _all_pairs() -> list[tuple[str, str, str]]:
    found = []
    for label, build in BY_HAND:
        for question, answer in build():
            found.append((label, question, answer))
    return found


class EveryPairIsSafeToTrainOnTest(unittest.TestCase):
    def test_every_answer_carries_the_disclaimer(self) -> None:
        missing = [
            f"{label}: {question}"
            for label, question, answer in _all_pairs()
            if SKINCARE_DISCLAIMER.lower() not in answer.lower()
        ]
        self.assertEqual(
            missing,
            [],
            "answers with no disclaimer — wrap them in _close(): " + str(missing),
        )

    def test_no_answer_is_empty(self) -> None:
        empty = [q for _l, q, a in _all_pairs() if not a.strip()]
        self.assertEqual(empty, [], f"empty answers: {empty}")

    def test_every_question_is_asked_once(self) -> None:
        asked = [q.strip().lower() for _l, q, _a in _all_pairs()]
        twice = sorted({q for q in asked if asked.count(q) > 1})
        self.assertEqual(twice, [], f"asked more than once: {twice}")

    def test_no_two_questions_are_the_same_question(self) -> None:
        """Different wording, same question, is still two answers to one.

        Word overlap rather than exact text, because "Do people with dark
        skin need sunscreen?" and "Do people with darker skin need to
        wear sunscreen?" share no exact form and every meaningful word.

        The threshold is calibrated on the pairs listed beside
        SAME_QUESTION, not chosen by feel.

        Two questions that differ only by a single-character word are
        left alone. The ABCDE family — "What does A in ABCDE mean?"
        through E — is five deliberately separate questions, and overlap
        cannot tell them apart from a duplicate: the one token that
        differs is one letter long. Asking whether the difference is
        more than a letter can.
        """
        pairs = _all_pairs()
        close = []
        for index, (_label, first, _answer) in enumerate(pairs):
            for _l2, second, _a2 in pairs[index + 1:]:
                one, two = _stems(first), _stems(second)
                if not one or not two:
                    continue
                if len(one & two) / len(one | two) < SAME_QUESTION:
                    continue
                differing = one ^ two
                if differing and all(len(word) == 1 for word in differing):
                    continue
                close.append(f"{first!r} ~ {second!r}")
        self.assertEqual(
            close,
            [],
            "these ask the same thing twice; keep the better answer: " + str(close),
        )

if __name__ == "__main__":
    unittest.main()
