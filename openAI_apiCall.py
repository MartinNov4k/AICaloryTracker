import os
import json
import base64
import re
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from openai import OpenAI


def get_answer(
    user_note: str,
    image_bytes: Optional[bytes] = None,
    model: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Pošle instrukce (a případně fotku) do OpenAI a vrátí dict:
    {
      "items": [...],
      "assumptions": "...",
      "total": {...}
    }

    POŽADAVEK: model má vrátit JEN validní JSON dle schema_text.
    """

    load_dotenv()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Chybí OPENAI_API_KEY v prostředí nebo v .env")

    client = OpenAI(api_key=api_key)


    model = model or os.getenv("OPENAI_MODEL", "gpt-5-pro")

    
    data_url = None
    if image_bytes:
        data_url = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode("utf-8")

    schema_text = """
Vrať jediný validní JSON s tímto tvarem:
{
  "items": [
    {
      "name": "string",
      "confidence": 0.0..1.0,
      "portion_grams": number,
      "per_100g": {
        "calories": number,
        "protein_g": number,
        "carbs_g": number,
        "sugar_g": number,
        "fat_g": number
      },
      "notes": "string (volitelné)"
    }
  ],
  "assumptions": "string"
}
Bez komentářů, bez extra textu mimo JSON.
""".strip()

    prompt_text = (
        "Rozpoznej jídlo na fotce, rozděl na položky (ingredience/komponenty). "
        "Pokud není fotka, vycházej pouze z uživatelova upřesnění. "
        "Odhadni porci každé položky v gramech a nutriční hodnoty na 100 g "
        "(kcal, bílkoviny, sacharidy, tuky, cukr). "
        "Zahrň rozumný odhad omáček/dresinků, jsou-li pravděpodobné. "
        "pokud uživatel zadá přesně položku např. 26 g bilkovin pak do vysledku uvažuj jen ty bilkoviny"
        f"Uživatelovo upřesnění: {user_note}\n\n{schema_text}"
    )

    # Responses API: multimodální vstup
    content = [{"type": "input_text", "text": prompt_text}]
    if data_url:
        content.append({"type": "input_image", "image_url": data_url})

    resp = client.responses.create(
        model=model,
        input=[{"role": "user", "content": content}],
        temperature=0,
        max_output_tokens=900,
    )

    raw = (resp.output_text or "").strip()

    def extract_json(s: str) -> str:
        """Zkusí vytáhnout JSON i kdyby byl zabalený v ```json ... ```."""
        m = re.search(r"```(?:json)?\s*(\{.*\})\s*```", s, flags=re.S)
        if m:
            return m.group(1)
        i, j = s.find("{"), s.rfind("}")
        return s[i : j + 1] if (i != -1 and j != -1 and j > i) else s

    json_str = extract_json(raw)

    try:
        data: Dict[str, Any] = json.loads(json_str)
    except json.JSONDecodeError as e:
        # Pomůže debug: uvidíš, co to skutečně vrátilo
        raise RuntimeError(f"Model nevrátil validní JSON. Chyba: {e}\n--- RAW ---\n{raw}") from e

    # Dopočítat total lokálně
    total = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0, "sugar_g": 0.0}

    for it in data.get("items", []):
        g = float(it.get("portion_grams", 0) or 0)
        per100 = it.get("per_100g", {}) or {}
        for k in total:
            total[k] += float(per100.get(k, 0) or 0) * (g / 100.0)

    data["total"] = {k: round(v, 1) for k, v in total.items()}
    return data
