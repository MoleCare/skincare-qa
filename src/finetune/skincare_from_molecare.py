"""Build skincare Q&A from MoleCare open-source sources — do not invent a parallel KB.

Sources (local checkouts, same content as github.com/MoleCare):
- molecare-mcp/src/resources/medical-kb.ts
- molecare-webapp FAQ + chatbot copy
- molecare-mcp CONTRIBUTING.md (diagnosis boundary)
- ClaudeChatService scope/decline pattern
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from finetune.paths import MCP_KB, WEBAPP_I18N
from finetune.systems import SKINCARE_DISCLAIMER

_ENTRY_RE = re.compile(
    r"""(?P<key>"[^"]+"|\w+)\s*:\s*\{\s*
        term:\s*"(?P<term>(?:\\.|[^"\\])*)"\s*,\s*
        definition:\s*"(?P<definition>(?:\\.|[^"\\])*)"\s*,\s*
        details:\s*"(?P<details>(?:\\.|[^"\\])*)"\s*,\s*
        significance:\s*"(?P<significance>(?:\\.|[^"\\])*)"
    """,
    re.VERBOSE | re.DOTALL,
)

_EDUCATION_REWRITE = (
    (re.compile(r"\b[Bb]enign moles\b"), "Typical moles"),
    (re.compile(r"\bMost benign moles\b"), "Many typical moles"),
    (re.compile(r"\bare typically symmetric\b"), "are often symmetric"),
)


def _unescape(text: str) -> str:
    return text.replace(r"\"", '"').replace(r"\n", "\n")


def _educate(text: str) -> str:
    out = text
    for pattern, repl in _EDUCATION_REWRITE:
        out = pattern.sub(repl, out)
    return out


def _close(answer: str) -> str:
    body = answer.strip()
    if SKINCARE_DISCLAIMER.lower() in body.lower():
        return body
    return f"{body}\n\n{SKINCARE_DISCLAIMER}"


def parse_knowledge_base(ts_text: str) -> list[dict[str, str]]:
    start = ts_text.find("const KNOWLEDGE_BASE")
    end = ts_text.find("const RESOURCES")
    if start < 0 or end < 0:
        raise ValueError("medical-kb.ts is missing KNOWLEDGE_BASE / RESOURCES")
    block = ts_text[start:end]
    entries = []
    for match in _ENTRY_RE.finditer(block):
        entries.append(
            {
                "key": match.group("key").strip('"'),
                "term": _unescape(match.group("term")),
                "definition": _educate(_unescape(match.group("definition"))),
                "details": _educate(_unescape(match.group("details"))),
                "significance": _educate(_unescape(match.group("significance"))),
            }
        )
    if len(entries) < 8:
        raise ValueError(f"parsed only {len(entries)} KB entries — parser drift?")
    return entries


def pairs_from_kb(entries: list[dict[str, str]]) -> list[tuple[str, str]]:
    pairs: list[tuple[str, str]] = []
    for entry in entries:
        term = entry["term"]
        definition = entry["definition"]
        details = entry["details"]
        why = entry["significance"]
        pairs.append((f"What is {term}?", _close(f"{definition}. {details}")))
        pairs.append((f"Explain {term} in plain language.", _close(f"{definition}. {details}")))
        pairs.append((f"Why does {term} matter for skin checks?", _close(why)))
    return pairs


def pairs_from_resources() -> list[tuple[str, str]]:
    """Hard-coded from molecare-mcp RESOURCES — kept in lockstep with the TS file."""
    return [
        (
            "What is the ABCDE rule?",
            _close(
                "ABCDE is an educational checklist clinicians and self-checks use "
                "when looking at moles: Asymmetry, Border, Color, Diameter, and "
                "Evolution. It is a guide, not a score and not a diagnosis. Not "
                "every melanoma follows these features, and moles that show some "
                "of them are not automatically cancer. When in doubt, see a "
                "dermatologist."
            ),
        ),
        (
            "How do I use the ABCDE rule on a mole?",
            _close(
                "Look at one mole at a time. A — do the two halves match? "
                "B — are the edges smooth or irregular? C — one colour or several? "
                "D — wider than about 6 mm, or growing? E — has it changed in size, "
                "shape, colour, or symptoms (itch, bleed, crust)? Write down what "
                "you notice or photograph it. A clinician interprets the picture; "
                "the checklist does not."
            ),
        ),
        (
            "What does A in ABCDE mean?",
            _close(
                "A is Asymmetry: one half of the mole does not match the other. "
                "It is a feature to note and show a clinician, not a verdict."
            ),
        ),
        (
            "What does B in ABCDE mean?",
            _close(
                "B is Border: irregular, ragged, notched, or blurred edges. "
                "Smooth, even edges are more typical. Irregular borders are one "
                "thing clinicians assess."
            ),
        ),
        (
            "What does C in ABCDE mean?",
            _close(
                "C is Color: more than one shade, or uneven colour, including "
                "black, red, white, or blue areas. One even brown is more typical. "
                "Colour mix is a reason to get a clinician's view, not a label."
            ),
        ),
        (
            "What does D in ABCDE mean?",
            _close(
                "D is Diameter: many melanomas are larger than 6 mm (a pencil "
                "eraser) when found, but they can be smaller. Size alone does not "
                "tell you what a mole is."
            ),
        ),
        (
            "What does E in ABCDE mean?",
            _close(
                "E is Evolution: a change in size, shape, colour, height, or new "
                "symptoms such as bleeding, itching, or crusting. Change over time "
                "is one of the more important things to take to a clinician."
            ),
        ),
        (
            "When should I see a dermatologist?",
            _close(
                "Book promptly for a mole that is changing quickly, bleeds without "
                "injury, is a new fast-growing mark, a sore that has not healed in "
                "about three weeks, or a mole with several ABCDE features. Also "
                "worth an appointment: a new mole after age 30, a mole that looks "
                "unlike your others, a personal or family history of melanoma, "
                "many moles, or a history of blistering sunburns. Annual skin "
                "checks are reasonable for most adults. When in doubt, go."
            ),
        ),
        (
            "How do I protect my skin from the sun?",
            _close(
                "Use a broad-spectrum SPF 30+ every day, including cloudy days. "
                "Reapply about every two hours outdoors. Add a wide-brim hat, "
                "UV-blocking sunglasses, and shade between 10am and 4pm. Skip "
                "tanning beds. UV damage adds up over a lifetime; every skin type "
                "needs protection."
            ),
        ),
        (
            "What SPF should I use?",
            _close(
                "SPF 30 or higher, broad-spectrum (UVA and UVB), is the usual "
                "daily recommendation. SPF 50+ is useful for long outdoor time. "
                "Apply a generous amount 15–30 minutes before you go out, and "
                "reapply every two hours or after swimming or sweating."
            ),
        ),
        (
            "How often should I check my moles?",
            _close(
                "A monthly head-to-toe self-check is a common habit: scalp, "
                "between toes, back (use a mirror). Photograph moles you want to "
                "compare later. Pair that with a clinician exam — yearly for most "
                "people, more often if you have extra risk factors."
            ),
        ),
        (
            "What are Fitzpatrick skin types?",
            _close(
                "A six-type scale of how skin reacts to sun. I always burns, "
                "never tans; II usually burns; III sometimes burns; IV rarely "
                "burns; V very rarely; VI typically does not burn. Lighter types "
                "have a higher chance of sun damage. Every type still needs "
                "protection — skin cancer can occur on darker skin too."
            ),
        ),
        (
            "Do people with dark skin need sunscreen?",
            _close(
                "Yes. Darker skin types have more natural pigment, but UV still "
                "damages skin and skin cancers can be diagnosed later. Daily "
                "broad-spectrum SPF 30+ and shade during peak UV are still useful."
            ),
        ),
    ]


def pairs_diagnosis_boundary() -> list[tuple[str, str]]:
    """From molecare-mcp CONTRIBUTING.md: never imitate a diagnosis."""
    decline = _close(
        "I can't tell you what a mole is from a description or a photo. "
        "I don't diagnose. Use ABCDE as a way to notice features — asymmetry, "
        "irregular border, mixed colour, size over about 6 mm, and change — "
        "and take what you notice to a dermatologist or GP. If it is changing, "
        "bleeding, or worrying you, book that visit rather than waiting on an "
        "app answer."
    )
    return [
        ("Is this mole melanoma?", decline),
        ("Look at my photo. Is it cancer?", decline),
        ("So this is definitely fine, right?", decline),
        ("What's the diagnosis?", decline),
        ("Can you confirm this is just a normal mole?", decline),
        (
            "My mole is asymmetric and two colours. What is it?",
            _close(
                "Those are features on the ABCDE checklist (asymmetry and colour "
                "variation). They are reasons to have a clinician look — not a "
                "name I can give the mole. Photograph it, note when you first "
                "noticed the change, and book a dermatologist or GP."
            ),
        ),
        (
            "It bled a little yesterday. Should I ignore it?",
            _close(
                "A mole that bleeds without a clear injury is one of the reasons "
                "to see a clinician promptly. I can't say what it is. Get it "
                "checked rather than watching and waiting on my answer."
            ),
        ),
        (
            "Write me a python script to sort files.",
            "I'm MoleCare's skin-health assistant, so I stay on dermatology and "
            "the app. I can help with moles, ABCDE, sun safety, skincare, or "
            f"how to use MoleCare. What would you like to know?\n\n{SKINCARE_DISCLAIMER}",
        ),
        (
            "Who won the election?",
            "I'm MoleCare's skin-health assistant, so I stay on dermatology "
            "topics. Happy to help with moles, skin-cancer prevention, sun "
            f"safety, or the MoleCare app.\n\n{SKINCARE_DISCLAIMER}",
        ),
    ]


def pairs_from_webapp(path: Path) -> list[tuple[str, str]]:
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    faq = data.get("faq") or {}
    pairs: list[tuple[str, str]] = []
    mapped = (
        ("whatIsMoleCare", "whatIsMoleCareAnswer"),
        ("howMuch", "howMuchAnswer"),
        ("isDataPrivate", "isDataPrivateAnswer"),
        ("multipleDevices", "multipleDevicesAnswer"),
        ("languages", "languagesAnswer"),
        ("question2", "answer2"),
    )
    for qk, ak in mapped:
        question, answer = faq.get(qk), faq.get(ak)
        if question and answer:
            pairs.append((question, _close(answer)))
    return pairs


def pairs_everyday_skincare() -> list[tuple[str, str]]:
    """Everyday product questions — still educational, still no diagnosis."""
    return [
        (
            "What does niacinamide do in a moisturizer?",
            _close(
                "Niacinamide (vitamin B3) is used to support the skin barrier, "
                "reduce the look of pores and uneven tone, and play well with "
                "most other actives. Typical leave-on strengths are around 4–5%. "
                "It is not a treatment for a changing mole — keep photographing "
                "and checking those separately."
            ),
        ),
        (
            "Can I use retinol and vitamin C in the same routine?",
            _close(
                "Many people use vitamin C in the morning (then SPF) and retinol "
                "at night. Using strong versions together can irritate. If your "
                "skin stings or peels, alternate nights or drop the strength. "
                "Retinoids are a reason to be extra strict with sunscreen. This "
                "is general product education, not a prescription."
            ),
        ),
        (
            "How do I start tretinoin without wrecking my barrier?",
            _close(
                "A common approach: pea-size for the whole face, two or three "
                "nights a week, over moisturizer if you are sensitive, then "
                "build up. Expect dryness. Daily SPF is required. Pause and "
                "see a clinician if you have severe irritation, or if you are "
                "pregnant or trying — tretinoin is not used in pregnancy. I "
                "can't prescribe or adjust your dose."
            ),
        ),
        (
            "What order should I layer cleanser, serum, moisturizer, SPF?",
            _close(
                "AM: cleanse, water-based serum, moisturizer, then sunscreen "
                "as the last leave-on. PM: cleanse, treatments (retinoid or "
                "acids), then moisturizer. Wait a minute between stingy layers "
                "if you need to. SPF is the step that actually cuts UV damage."
            ),
        ),
        (
            "I have oily, breakout-prone skin. What should a simple routine look like?",
            _close(
                "Keep it short: a gentle cleanser, a lightweight moisturizer "
                "(skipping moisturizer often makes oil worse), and SPF 30+ every "
                "morning. Salicylic acid or benzoyl peroxide can help spots; "
                "introduce one at a time. If cysts, scarring, or sudden adult "
                "acne show up, that is clinician territory."
            ),
        ),
        (
            "I have dry, tight skin. What should I change?",
            _close(
                "Use a cream cleanser or just water in the morning, a cream "
                "with ceramides or glycerin, and skip daily strong acids. "
                "Occlusive last at night if you are flaky. Check that your "
                "retinoid frequency isn't the cause. Persistent redness, "
                "cracking, or suspected eczema needs a clinician."
            ),
        ),
        (
            "Is hyaluronic acid enough as a moisturizer?",
            _close(
                "Usually not on its own. Hyaluronic acid holds water; in dry air "
                "it can feel tight unless you seal it with a cream. Use it on "
                "damp skin, then moisturizer, then SPF in the morning."
            ),
        ),
        (
            "Can I use AHA or BHA with tretinoin?",
            _close(
                "Both increase irritation. Many people keep acids to mornings "
                "or to nights they skip the retinoid. If you peel or burn, "
                "stop the extra acid. Sunscreen every day. Ask a clinician "
                "before combining prescription tretinoin with strong peels."
            ),
        ),
        (
            "What moisturizer ingredients help a damaged barrier?",
            _close(
                "Look for ceramides, cholesterol, fatty acids, glycerin, and "
                "petrolatum or dimethicone to seal. Pause actives (retinoid, "
                "acids, strong vitamin C) until stinging stops. If the skin "
                "is swollen, oozing, or painful, get medical care — that is "
                "beyond routine dryness."
            ),
        ),
        (
            "Do I need sunscreen indoors?",
            _close(
                "UVA still comes through many windows. If you sit by a window "
                "or go in and out, a morning SPF 30+ is a simple habit. It is "
                "also the most useful melanoma-prevention step in a routine."
            ),
        ),
    ]


def all_pairs(kb_path: Path = MCP_KB, i18n_path: Path = WEBAPP_I18N) -> list[tuple[str, str]]:
    if not kb_path.is_file():
        raise FileNotFoundError(
            f"molecare-mcp knowledge base not found: {kb_path}\n"
            "Expected a local clone of https://github.com/MoleCare/molecare-mcp"
        )
    entries = parse_knowledge_base(kb_path.read_text(encoding="utf-8"))
    pairs = [
        *pairs_from_kb(entries),
        *pairs_from_resources(),
        *pairs_diagnosis_boundary(),
        *pairs_from_webapp(i18n_path),
        *pairs_everyday_skincare(),
    ]
    seen: set[tuple[str, str]] = set()
    unique: list[tuple[str, str]] = []
    for pair in pairs:
        if pair in seen:
            continue
        seen.add(pair)
        unique.append(pair)
    return unique
