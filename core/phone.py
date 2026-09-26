import re

DEFAULT_COUNTRY_CODE = "237"


def normalize_phone(raw: str) -> str:
    """Normalise un numéro de téléphone en E.164 "best effort" (Cameroun, +237 par défaut).

    Ne rejette pas les formats non reconnus : nettoie la ponctuation et
    ajoute l'indicatif par défaut si absent, sans validation stricte
    (voir design.md du changement add-client-and-credit-sale).
    """
    digits = re.sub(r"[^\d+]", "", raw or "")

    if digits.startswith("00"):
        digits = "+" + digits[2:]

    if digits.startswith("+"):
        return digits

    if digits.startswith(DEFAULT_COUNTRY_CODE):
        return "+" + digits

    return "+" + DEFAULT_COUNTRY_CODE + digits
