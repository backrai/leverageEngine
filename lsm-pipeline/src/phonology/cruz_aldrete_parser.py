"""
Cruz Aldrete Notation → LSM-PN Converter
Parses Cruz Aldrete's transcription notation (e.g. "1234+/a+") into
structured LSM-PN HandshapeSpec objects.

Notation system from: Cruz Aldrete (2008) §4.2.5, pp. 325-329
"""
import re
import json
from dataclasses import dataclass, asdict
from typing import Optional

from .enums import FlexionLevel, ThumbOpposition, FingerSpread, FingerInteraction


# ── Notation Symbol Maps ─────────────────────────────────────────────────────

POSTURE_MAP = {
    "+":  FlexionLevel.EXTENDED,    # abierto
    "°":  FlexionLevel.CURVED,      # redondeado
    "^":  FlexionLevel.BENT,        # aplanado
    "-":  FlexionLevel.CLOSED,      # cerrado
    '"':  FlexionLevel.BENT,        # agrapado (hooked → BENT, with DIP note)
    "¬":  FlexionLevel.BENT,        # acantilado (cliff → BENT)
    "‖":  FlexionLevel.BENT,        # variant bent notation
}

THUMB_ROTATION_MAP = {
    "o": ThumbOpposition.OPPOSED,
    "a": ThumbOpposition.PARALLEL,
}

INTERACTION_MAP = {
    "sep":  FingerInteraction.SPREAD,
    "apil": FingerInteraction.STACKED,
    "crz":  FingerInteraction.CROSSED,
}

# Cruz Aldrete location codes → (body_region, anchor_name, latin_name)
LOCATION_MAP = {
    # Head, Face & Neck (31)
    "Ca": ("HEAD", "Head", "caput"),
    "Fa": ("FACE", "Face", "facies"),
    "Vx": ("HEAD", "Crown", "vertex"),
    "Ce": ("NECK", "Nape", "cervix"),
    "Te": ("HEAD", "Temple", "tempus"),
    "Fr": ("FACE", "Forehead", "frons"),
    "IpsiFr": ("FACE", "Forehead-ipsilateral", None),
    "XFr": ("FACE", "Forehead-contralateral", None),
    "Au": ("HEAD", "Ear", "auris"),
    "LobAu": ("HEAD", "Earlobe", None),
    "Na": ("FACE", "Nose-tip", "nasus"),
    "Sep": ("FACE", "Nose-bridge", "septum"),
    "AlNa": ("FACE", "Nasal-wings", None),
    "Ci": ("FACE", "Eyebrow", "cilium"),
    "Su": ("FACE", "Eyebrow", "cilium"),
    "Cin": ("FACE", "Brow-ridge", "cinnus"),
    "Oc": ("FACE", "Eye", "oculus"),
    "RapOc": ("FACE", "Eye-corner", "rapum oculus"),
    "OrbOc": ("FACE", "Eye-orbit", None),
    "Po": ("FACE", "Cheekbone", "pomulum"),
    "Ge": ("FACE", "Cheek", "gena"),
    "Os": ("FACE", "Mouth", "os"),
    "IpsiOs": ("FACE", "Mouth-ipsilateral", None),
    "XOs": ("FACE", "Mouth-contralateral", None),
    "Lin": ("FACE", "Tongue", "lingua"),
    "La": ("FACE", "Lips", "labium"),
    "Lab": ("FACE", "Lips", "labium"),
    "Me": ("FACE", "Chin", "mentum"),
    "Gu": ("NECK", "Below-chin", "guttur"),
    "Co": ("NECK", "Neck", "collum"),
    "IpsiCo": ("NECK", "Neck-ipsilateral", None),
    "Den": ("FACE", "Teeth", "dentia"),
    "Col": ("FACE", "Canine-tooth", None),
    "MedDen": ("FACE", "Incisors", "medii dentes"),
    "Par": ("HEAD", "Parietal", "parietalis"),
    # Trunk & Legs (17)
    "Um": ("TRUNK", "Shoulder", "umerus"),
    "Pe": ("TRUNK", "Chest", "pectus"),
    "XPe": ("TRUNK", "Chest-contralateral", None),
    "IpsiPe": ("TRUNK", "Chest-ipsilateral", None),
    "Cor": ("TRUNK", "Heart", "cor"),
    "Es": ("TRUNK", "Sternum", None),
    "To": ("TRUNK", "Thorax", None),
    "Ve": ("TRUNK", "Stomach", "venter"),
    "Abd": ("TRUNK", "Abdomen", None),
    "Cit": ("TRUNK", "Waist", "cinctura"),
    "Cox": ("TRUNK", "Hip", "coxa"),
    "Fe": ("TRUNK", "Thigh", "femur"),
    "Gen": ("TRUNK", "Knee", "genu"),
    "Cos": ("TRUNK", "Ribs", "costae"),
    "Cla": ("TRUNK", "Clavicle", "clavicula"),
    "Dor": ("TRUNK", "Back", "dorsum"),
    "Je": ("TRUNK", "Liver", "jecur"),
    # Arm & Forearm (11)
    "Br": ("ARM", "Arm-upper", "bracchium"),
    "IntBr": ("ARM", "Arm-interior", None),
    "IntAbr": ("FOREARM", "Forearm-interior", None),
    "InfAbr": ("FOREARM", "Forearm-lower", None),
    "RAAbr": ("FOREARM", "Forearm-radial", None),
    "ExtAbr": ("FOREARM", "Forearm-exterior", None),
    "Abr": ("FOREARM", "Forearm", None),
    "Cut": ("ARM", "Elbow", "cubitus"),
    "Car": ("HAND", "Wrist", "carpus"),
    "ExtCar": ("HAND", "Wrist-exterior", None),
    "IntCar": ("HAND", "Wrist-interior", None),
    # Hand & Fingers (17)
    "Palma": ("HAND", "Palm", None),
    "ExtMano": ("HAND", "Back-of-hand", None),
    "Dorso": ("HAND", "Back-of-hand", None),
    "D1": ("HAND", "Index-finger", None),
    "D2": ("HAND", "Middle-finger", None),
    "D3": ("HAND", "Ring-finger", None),
    "D4": ("HAND", "Pinky-finger", None),
    "PuntDed": ("HAND", "Fingertips", None),
    "Pol": ("HAND", "Thumb", "pollex"),
    "IntDed": ("HAND", "Fingers-interior", None),
    "ExtDed": ("HAND", "Fingers-exterior", None),
    "Nod": ("HAND", "Knuckles", "nodus"),
    "Base": ("HAND", "Hand-base", None),
    "Cub": ("HAND", "Ulnar-side", None),
    "RA": ("HAND", "Radial-side", None),
    "Gem": ("HAND", "Fingertip-pad", "gemma"),
    "Ung": ("HAND", "Nail", "unguis"),
}

# Contour movement codes
CONTOUR_MAP = {
    "lin": "STRAIGHT",
    "arc": "ARC",
    "circ": "CIRCLE",
    "zig": "ZIGZAG",
    "7": "SEVEN",
}

# Local movement codes
LOCAL_MAP = {
    "ond": "WIGGLE",
    "cir": "CIRCULAR",
    "rot": "TWIST",
    "rsc": "SCRATCH",
    "cab": "NOD",
    "osc": "OSCILLATE",
    "solt": "RELEASE",
    "apl": "FLATTEN",
    "prog": "PROGRESSIVE",
    "vib": "VIBRATE",
    "frot": "RUB",
}


# ── Parser ───────────────────────────────────────────────────────────────────

@dataclass
class ParsedCM:
    """Result of parsing a Cruz Aldrete CM notation string."""
    selected_fingers: list[int]
    finger_posture: FlexionLevel
    finger_spread: FingerSpread
    finger_interaction: FingerInteraction
    non_selected_above: bool
    thumb_opposition: ThumbOpposition
    thumb_flexion: FlexionLevel
    thumb_contact: bool
    distal_override: Optional[str]
    raw_notation: str

    def to_lsm_pn(self) -> dict:
        """Convert to LSM-PN HandshapeSpec dict."""
        # Map finger states: selected fingers get the posture, others get CLOSED
        states = {}
        finger_names = {1: "index", 2: "middle", 3: "ring", 4: "pinky"}
        for num, name in finger_names.items():
            if num in self.selected_fingers:
                states[name] = self.finger_posture.value
            else:
                states[name] = FlexionLevel.CLOSED.value

        return {
            "finger_states": states,
            "thumb_opposition": self.thumb_opposition.value,
            "thumb_flexion": self.thumb_flexion.value,
            "selected_fingers": self.selected_fingers,
            "spread": self.finger_spread.value,
            "interaction": self.finger_interaction.value,
            "thumb_contact": self.thumb_contact,
            "non_selected_above": self.non_selected_above,
        }


def parse_cm_notation(notation: str) -> ParsedCM:
    """
    Parse a Cruz Aldrete CM notation string into structured data.

    Format: [fingers][posture][modifiers]/[thumb_rotation][thumb_posture][thumb_modifiers]

    Examples:
        "1234+/a+"  → all fingers extended, thumb aligned extended
        "12+sep/o-" → index+middle extended spread, thumb opposed closed
        "1^°NSAb-/o^c+" → index curved, NSAb closed, thumb opposed bent, contact
    """
    raw = notation.strip()

    # Split on '/'
    if "/" not in raw:
        raise ValueError(f"Invalid CM notation (no '/' separator): {raw}")

    finger_part, thumb_part = raw.split("/", 1)

    # ── Parse finger part ────────────────────────────────────────────────
    # Extract selected finger numbers
    finger_nums = []
    i = 0
    while i < len(finger_part) and finger_part[i] in "1234":
        finger_nums.append(int(finger_part[i]))
        i += 1

    if not finger_nums:
        raise ValueError(f"No finger numbers found in: {raw}")

    remainder = finger_part[i:]

    # Extract posture (first posture symbol after numbers)
    posture = FlexionLevel.EXTENDED  # default
    for symbol, level in POSTURE_MAP.items():
        if remainder.startswith(symbol):
            posture = level
            remainder = remainder[len(symbol):]
            break

    # Check for secondary posture modifier (e.g., +° means curved after extended)
    for symbol, level in POSTURE_MAP.items():
        if remainder.startswith(symbol) and symbol in ("°", "^"):
            posture = level  # override with more specific
            remainder = remainder[len(symbol):]
            break

    # Check for interaction modifiers
    interaction = FingerInteraction.NONE
    spread = FingerSpread.NEUTRAL
    for key, val in INTERACTION_MAP.items():
        if key in remainder:
            interaction = val
            if val == FingerInteraction.SPREAD:
                spread = FingerSpread.SPREAD
            remainder = remainder.replace(key, "", 1)
            break

    # Check for NSAb (non-selected above)
    nsab = "NSAb" in remainder
    if nsab:
        remainder = remainder.replace("NSAb", "")
        # Clean up any leftover +/- after NSAb
        remainder = remainder.lstrip("+-")

    # ── Parse thumb part ─────────────────────────────────────────────────
    thumb_opp = ThumbOpposition.OPPOSED  # default
    thumb_flex = FlexionLevel.EXTENDED   # default
    thumb_contact = False
    distal = None

    t = thumb_part

    # Thumb rotation
    if t and t[0] in THUMB_ROTATION_MAP:
        thumb_opp = THUMB_ROTATION_MAP[t[0]]
        t = t[1:]

    # Thumb posture
    for symbol, level in POSTURE_MAP.items():
        if t.startswith(symbol):
            thumb_flex = level
            t = t[len(symbol):]
            break

    # Check for secondary thumb posture
    for symbol, level in POSTURE_MAP.items():
        if t.startswith(symbol) and symbol in ("°", "^", "+", "-"):
            # Only override if it's a distinct modifier
            break

    # Distal override
    if "d+" in t:
        distal = "d+"
        t = t.replace("d+", "")
    elif "d-" in t:
        distal = "d-"
        t = t.replace("d-", "")
    elif "d°" in t:
        distal = "d°"
        t = t.replace("d°", "")

    # Contact
    if "c+" in t:
        thumb_contact = True
        t = t.replace("c+", "")

    return ParsedCM(
        selected_fingers=finger_nums,
        finger_posture=posture,
        finger_spread=spread,
        finger_interaction=interaction,
        non_selected_above=nsab,
        thumb_opposition=thumb_opp,
        thumb_flexion=thumb_flex,
        thumb_contact=thumb_contact,
        distal_override=distal,
        raw_notation=raw,
    )


def parse_location(loc_code: str) -> dict:
    """Parse a Cruz Aldrete location code to LSM-PN LocationSpec."""
    # Handle space location codes (e.g., "mØTo" = medio, vector 0, thorax height)
    space_match = re.match(r"([pmd])(\d?)([A-Z][a-z]*)", loc_code)
    if loc_code.startswith("m") and space_match:
        distance_map = {"p": "PROXIMAL", "m": "MEDIAL", "d": "DISTAL"}
        dist = distance_map.get(space_match.group(1), "MEDIAL")
        vector = f"V{space_match.group(2) or '0'}"
        height = space_match.group(3)
        return {
            "body_anchor": loc_code,
            "body_region": "NEUTRAL_SPACE",
            "space_vector": vector,
            "space_distance": dist,
        }

    # Handle body location codes
    if loc_code in LOCATION_MAP:
        region, name, latin = LOCATION_MAP[loc_code]
        result = {
            "body_anchor": loc_code,
            "body_region": region,
        }
        return result

    # Unknown — return as-is
    return {"body_anchor": loc_code, "body_region": "UNKNOWN"}


def parse_contour(code: str) -> Optional[str]:
    """Parse a Cruz Aldrete contour movement code."""
    return CONTOUR_MAP.get(code.lower())


def parse_local(code: str) -> Optional[str]:
    """Parse a Cruz Aldrete local movement code."""
    return LOCAL_MAP.get(code.lower())


# ── Convenience: Full sign notation → LSM-PN ────────────────────────────────

def notation_to_lsm_pn(
    sign_id: str,
    gloss: str,
    cm_notation: str,
    location_code: str,
    contour_code: Optional[str] = None,
    local_code: Optional[str] = None,
    cm_id: Optional[int] = None,
) -> dict:
    """
    Convert Cruz Aldrete notation components into a minimal LSM-PN document.

    Args:
        sign_id: Unique ID (e.g. "LSM_CASA_001")
        gloss: Spanish gloss
        cm_notation: CM notation string (e.g. "1234+/a+")
        location_code: Location code (e.g. "Pe", "Fr", "mØTo")
        contour_code: Optional contour movement (e.g. "lin", "arc")
        local_code: Optional local movement (e.g. "rot", "ond")
        cm_id: Optional CM inventory number (1-101)
    """
    parsed_cm = parse_cm_notation(cm_notation)
    handshape = parsed_cm.to_lsm_pn()
    if cm_id:
        handshape["cm_id"] = cm_id
    handshape["cruz_aldrete_notation"] = cm_notation

    location = parse_location(location_code)

    movement = {}
    if contour_code:
        movement["contour"] = parse_contour(contour_code)
    if local_code:
        movement["local"] = parse_local(local_code)

    return {
        "meta": {
            "schema_version": "1.0",
            "sign_id": sign_id,
            "gloss": gloss,
        },
        "dominant_hand": {
            "handshape": handshape,
            "location": location,
            "movement": movement if movement else None,
        },
        "timing": {
            "phases": ["PREPARATION", "STROKE", "HOLD", "RETRACTION"],
        },
    }


# ── CLI ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Quick demo: parse some CM notations
    test_notations = [
        "1234+/a+",       # CM#1 BIEN
        "12+sep/o-",      # CM#38 LETRA-V
        "1+/o-",          # CM#55 CL:PERSONA
        "1^°NSAb-/o^c+",  # CM#69 LETRA-F
        "1234-/a+",       # CM#10 LETRA-A
    ]

    for notation in test_notations:
        parsed = parse_cm_notation(notation)
        lsm_pn = parsed.to_lsm_pn()
        print(f"\n{notation}:")
        print(json.dumps(lsm_pn, indent=2))
