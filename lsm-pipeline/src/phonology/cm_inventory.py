"""
LSM Handshape (CM) Inventory — All 101 Configurations
Source: Cruz Aldrete (2008) Gramática de la LSM, Tabla 4.11, pp. 329-331

Each CM is parsed from Cruz Aldrete notation into:
  - finger_states: per-finger flexion level (EXTENDED/CURVED/BENT/CLOSED)
  - thumb_opposition: OPPOSED (o) or PARALLEL (a)
  - thumb_flexion: thumb's own flexion level
  - spread: finger spread state
  - interaction: special finger arrangement (stacked, crossed, etc.)
  - selected_fingers: which fingers are active
  - frequency_tier: 1 (high) to 4 (rare) for implementation priority
"""
from dataclasses import dataclass, field
from typing import Optional

from .enums import FlexionLevel as FL, ThumbOpposition, FingerSpread, FingerInteraction


E = FL.EXTENDED   # + (abierto)    = 0%
C = FL.CURVED     # ° (redondeado) = 33%
B = FL.BENT       # ^ (aplanado)   = 66%
X = FL.CLOSED     # - (cerrado)    = 100%

OPP = ThumbOpposition.OPPOSED    # o
PAR = ThumbOpposition.PARALLEL   # a

SPREAD = FingerSpread.SPREAD
NEUTRAL = FingerSpread.NEUTRAL
CLOSED_SP = FingerSpread.CLOSED


@dataclass
class CMEntry:
    """A single handshape configuration in the LSM inventory."""
    cm_id: int                                    # 1-101
    cruz_aldrete_notation: str                     # e.g. "1234+/a+"
    example_sign: str                              # primary example gloss
    alpha_code: Optional[str]                      # e.g. "[5']", "[B]", or None

    # Finger states for the 4 non-thumb fingers
    index: FL                                      # D1
    middle: FL                                     # D2
    ring: FL                                       # D3
    pinky: FL                                      # D4

    # Which fingers are "selected" (active in the sign)
    selected_fingers: list[int]                    # subset of [1,2,3,4]

    # Thumb
    thumb_opposition: ThumbOpposition
    thumb_flexion: FL

    # Modifiers
    spread: FingerSpread = NEUTRAL
    interaction: FingerInteraction = FingerInteraction.NONE
    non_selected_above: bool = False               # NSAb
    thumb_contact: bool = False                    # c+
    distal_override: Optional[str] = None          # d+, d-

    # Implementation priority (not exclusion)
    frequency_tier: int = 2                        # 1=high, 2=medium, 3=low, 4=rare

    # Notes
    notes: str = ""


# ═══════════════════════════════════════════════════════════════════════════════
# FULL INVENTORY: 101 CMs
# ═══════════════════════════════════════════════════════════════════════════════

CM_INVENTORY: list[CMEntry] = [
    # ── GROUP A: All Fingers (1234) — CMs #1-30 ─────────────────────────────

    CMEntry(1,  "1234+/a+",       "BIEN",             "[5']",
            E, E, E, E, [1,2,3,4], PAR, E, frequency_tier=1),
    CMEntry(2,  "1234+/a^",       "MÁS",              "[B]",
            E, E, E, E, [1,2,3,4], PAR, B, frequency_tier=1),
    CMEntry(3,  "1234+/o+",       "COLIMA-1",         None,
            E, E, E, E, [1,2,3,4], OPP, E, frequency_tier=2),
    CMEntry(4,  "1234+/o-",       "LETRA-B",          "[B']",
            E, E, E, E, [1,2,3,4], OPP, X, frequency_tier=1),
    CMEntry(5,  "1234+/o^",       "BUENO",            None,
            E, E, E, E, [1,2,3,4], OPP, B, frequency_tier=2),
    CMEntry(6,  "1234+°/a°",      "TORTUGA-MD",       None,
            C, C, C, C, [1,2,3,4], PAR, C, frequency_tier=2),
    CMEntry(7,  "1234\"°/o°",     "LETRA-C",          "[C]",
            C, C, C, C, [1,2,3,4], OPP, C, frequency_tier=1),
    CMEntry(8,  "1234+°/o°d-y-",  "LETRA-O",          "[O]",
            C, C, C, C, [1,2,3,4], OPP, C, frequency_tier=1,
            thumb_contact=True, distal_override="d-",
            notes="Thumb distal phalanx flexed, non-tip contact"),
    CMEntry(9,  "1234-/o-",       "LETRA-S",          "[S]",
            X, X, X, X, [1,2,3,4], OPP, X, frequency_tier=1),
    CMEntry(10, "1234-/a+",       "LETRA-A",          "[A]",
            X, X, X, X, [1,2,3,4], PAR, E, frequency_tier=1),
    CMEntry(11, "1234¬/o^",       "SOLDADO",          None,
            B, B, B, B, [1,2,3,4], OPP, B, frequency_tier=3,
            notes="Acantilado (cliff) posture — mapped to BENT"),
    CMEntry(12, "1234-/a+d-",     "BOLÍGRAFO",        None,
            X, X, X, X, [1,2,3,4], PAR, E, frequency_tier=2,
            distal_override="d-"),
    CMEntry(13, "1234-/a+d+",     "NO-HABER-2",       None,
            X, X, X, X, [1,2,3,4], PAR, E, frequency_tier=2,
            distal_override="d+"),
    CMEntry(14, "1234^/a+",       "LLAMAR-LA-ATENCIÓN", None,
            B, B, B, B, [1,2,3,4], PAR, E, frequency_tier=2),
    CMEntry(15, "1234^/a^",       "CUCHARA",          None,
            B, B, B, B, [1,2,3,4], PAR, B, frequency_tier=2),
    CMEntry(16, "1234^/o+c+",     "COLIMA-2",         None,
            B, B, B, B, [1,2,3,4], OPP, E, frequency_tier=2,
            thumb_contact=True),
    CMEntry(17, "1234^/o+",       "CL:LIBRO",         "[B̂]",
            B, B, B, B, [1,2,3,4], OPP, E, frequency_tier=1),
    CMEntry(18, "1234^crz/o+c+",  "VIVIR",            "[5̂]",
            B, B, B, B, [1,2,3,4], OPP, E, frequency_tier=2,
            interaction=FingerInteraction.CROSSED, thumb_contact=True),
    CMEntry(19, "1234\"/a^d-",    "LETRA-E",          "[E]",
            B, B, B, B, [1,2,3,4], PAR, B, frequency_tier=1,
            distal_override="d-",
            notes="Hooked (agrapado) — DIP flexed independently"),
    CMEntry(20, "1234+sep/a+",    "NÚM.5",            "[5]",
            E, E, E, E, [1,2,3,4], PAR, E, spread=SPREAD, frequency_tier=1),
    CMEntry(21, "1234+sep/o-",    "NÚM.4",            "[4]",
            E, E, E, E, [1,2,3,4], OPP, X, spread=SPREAD, frequency_tier=1),
    CMEntry(22, "1234+sep/o+",    "COPIAR-MA",        None,
            E, E, E, E, [1,2,3,4], OPP, E, spread=SPREAD, frequency_tier=2),
    CMEntry(23, "1234^sep/a+",    "TIRAR-2",          None,
            B, B, B, B, [1,2,3,4], PAR, E, spread=SPREAD, frequency_tier=2),
    CMEntry(24, "1234+°sep/a+",   "GATO",             None,
            C, C, C, C, [1,2,3,4], PAR, E, spread=SPREAD, frequency_tier=2),
    CMEntry(25, "1234\"sep/a+d-", "TRISTE-2",         None,
            B, B, B, B, [1,2,3,4], PAR, E, spread=SPREAD, frequency_tier=3,
            distal_override="d-"),
    CMEntry(26, "1234+°sep/o°",   "GRITAR",           "[5̃]",
            C, C, C, C, [1,2,3,4], OPP, C, spread=SPREAD, frequency_tier=2),
    CMEntry(27, "1234\"°sep/o+d-","MARCHITAR",         None,
            C, C, C, C, [1,2,3,4], OPP, E, spread=SPREAD, frequency_tier=3,
            distal_override="d-"),
    CMEntry(28, "1234\"°sep/o-",  "CUARTO-ORD-2",     None,
            C, C, C, C, [1,2,3,4], OPP, X, spread=SPREAD, frequency_tier=3),
    CMEntry(29, "1234^apil/o^",   "ARAÑA-2",          None,
            B, B, B, B, [1,2,3,4], OPP, B,
            interaction=FingerInteraction.STACKED, frequency_tier=3),
    CMEntry(30, "1234-/o- ps",    "NÚM.9",            None,
            X, X, X, X, [1,2,3,4], OPP, X, frequency_tier=2,
            notes="ps = prensado (pinch contact)"),

    # ── GROUP B: Three Fingers (123) — CMs #31-36 ───────────────────────────

    CMEntry(31, "123+/o-",        "MANZANA",          None,
            E, E, E, X, [1,2,3], OPP, X, frequency_tier=2),
    CMEntry(32, "123+sep/o-",     "NÚM.3",            "[3]",
            E, E, E, X, [1,2,3], OPP, X, spread=SPREAD, frequency_tier=1),
    CMEntry(33, "123+NSAb+/a+",   "LETRA-M",          "[M]",
            E, E, E, X, [1,2,3], PAR, E, frequency_tier=1,
            non_selected_above=True),
    CMEntry(34, "123^/o-",        "MIÉRCOLES",        None,
            B, B, B, X, [1,2,3], OPP, X, frequency_tier=2),
    CMEntry(35, "12+sep/a+",      "FILMAR",           None,
            E, E, X, X, [1,2], PAR, E, spread=SPREAD, frequency_tier=2,
            notes="Listed in 123 group but only 12 selected"),
    CMEntry(36, "12+/a+",         "LETRA-H",          "[H]",
            E, E, X, X, [1,2], PAR, E, frequency_tier=1,
            notes="Listed in 123 group but only 12 selected"),

    # ── GROUP C: Two Fingers (12) — CMs #37-53 ──────────────────────────────

    CMEntry(37, "12+/o-",         "LETRA-U",          "[2]",
            E, E, X, X, [1,2], OPP, X, frequency_tier=1),
    CMEntry(38, "12+sep/o-",      "LETRA-V",          "[V]",
            E, E, X, X, [1,2], OPP, X, spread=SPREAD, frequency_tier=1),
    CMEntry(39, "12+sep/o+",      "NO-1",             None,
            E, E, X, X, [1,2], OPP, E, spread=SPREAD, frequency_tier=1),
    CMEntry(40, "12+°sep/o-",     "CL:PERSONA-RODILLAS","[V┐]",
            C, C, X, X, [1,2], OPP, X, spread=SPREAD, frequency_tier=2),
    CMEntry(41, "12^sep/o-",      "VER",              None,
            B, B, X, X, [1,2], OPP, X, spread=SPREAD, frequency_tier=1),
    CMEntry(42, "12\"sep/o-",     "PESERO",           None,
            B, B, X, X, [1,2], OPP, X, spread=SPREAD, frequency_tier=3,
            notes="Hooked posture"),
    CMEntry(43, "12+°apil/o+c+",  "LETRA-D",          "[D]",
            C, C, X, X, [1,2], OPP, E,
            interaction=FingerInteraction.STACKED, thumb_contact=True, frequency_tier=1),
    CMEntry(44, "12+apil/o^",     "LETRA-P",          "[P]",
            E, E, X, X, [1,2], OPP, B,
            interaction=FingerInteraction.STACKED, frequency_tier=1),
    CMEntry(45, "12+crz/o-",      "LETRA-R",          "[R]",
            E, E, X, X, [1,2], OPP, X,
            interaction=FingerInteraction.CROSSED, frequency_tier=1),
    CMEntry(46, "12+crz/a+",      "SOLTERO",          None,
            E, E, X, X, [1,2], PAR, E,
            interaction=FingerInteraction.CROSSED, frequency_tier=2),
    CMEntry(47, "12^crz/o-",      "ROPA",             None,
            B, B, X, X, [1,2], OPP, X,
            interaction=FingerInteraction.CROSSED, frequency_tier=2),
    CMEntry(48, "12^/o-",         "LETRA-N",          "[N]",
            B, B, X, X, [1,2], OPP, X, frequency_tier=1),
    CMEntry(49, "12^/o+",         "INTELIGENTE",      None,
            B, B, X, X, [1,2], OPP, E, frequency_tier=2),
    CMEntry(50, "12^°/o+c+",      "NO-2",             None,
            C, C, X, X, [1,2], OPP, E, thumb_contact=True, frequency_tier=2,
            notes="Bent+curved hybrid"),
    CMEntry(51, "12\"sep/o^",     "CL:ANIMAL-4-PATAS","[3̂]",
            B, B, X, X, [1,2], OPP, B, spread=SPREAD, frequency_tier=2,
            notes="Hooked posture"),
    CMEntry(52, "12\"°/o+",       "BACARDI",          None,
            C, C, X, X, [1,2], OPP, E, frequency_tier=3),
    CMEntry(53, "12\"/o-",        "ESTE",             None,
            B, B, X, X, [1,2], OPP, X, frequency_tier=2,
            notes="Hooked posture"),

    # ── GROUP D: Index Finger (1) — CMs #54-74 ──────────────────────────────

    CMEntry(54, "1+/a+",          "LETRA-G",          "[G]",
            E, X, X, X, [1], PAR, E, frequency_tier=1),
    CMEntry(55, "1+/o-",          "CL:PERSONA",       "[1]",
            E, X, X, X, [1], OPP, X, frequency_tier=1),
    CMEntry(56, "1+/o+",          "LETRA-L",          "[L]",
            E, X, X, X, [1], OPP, E, frequency_tier=1),
    CMEntry(57, "1^/o^",          "NÚM.70",           None,
            B, X, X, X, [1], OPP, B, frequency_tier=3),
    CMEntry(58, "1\"°/o^d-c+y-",  "POCO-1",           None,
            C, X, X, X, [1], OPP, B, frequency_tier=3,
            thumb_contact=True, distal_override="d-"),
    CMEntry(59, "1\"^/a+",        "POCO-2",           None,
            B, X, X, X, [1], PAR, E, frequency_tier=3),
    CMEntry(60, "1^/o-c-",        "ÍNDICE→1",         None,
            B, X, X, X, [1], OPP, X, frequency_tier=2),
    CMEntry(61, "1^/o+c-",        "PEQUEÑO",          "[L̂]",
            B, X, X, X, [1], OPP, E, frequency_tier=2),
    CMEntry(62, "1^/o+c+",        "SARAMPIÓN",        None,
            B, X, X, X, [1], OPP, E, thumb_contact=True, frequency_tier=3),
    CMEntry(63, "1+°/o°+d-c+",    "NÚM.20",           None,
            C, X, X, X, [1], OPP, C, thumb_contact=True, frequency_tier=2,
            distal_override="d-"),
    CMEntry(64, "1\"°/o+",        "LETRA-Q",          "[L̃]",
            C, X, X, X, [1], OPP, E, frequency_tier=2),
    CMEntry(65, "1\"°/o-",        "AGUA",             None,
            C, X, X, X, [1], OPP, X, frequency_tier=2),
    CMEntry(66, "1¬/o^c+",        "SIGNIFICAR",       None,
            B, X, X, X, [1], OPP, B, thumb_contact=True, frequency_tier=2,
            notes="Cliff posture — mapped to BENT"),
    CMEntry(67, "1+°NSAb/o+°c+",  "NÚM.40",           None,
            C, X, X, X, [1], OPP, C,
            non_selected_above=True, thumb_contact=True, frequency_tier=3),
    CMEntry(68, "1-NSAb+/o-",     "LETRA-T",          "[T]",
            X, X, X, X, [1], OPP, X,
            non_selected_above=True, frequency_tier=1),
    CMEntry(69, "1^°NSAb-/o^c+",  "LETRA-F",          "[F]",
            C, X, X, X, [1], OPP, B,
            non_selected_above=True, thumb_contact=True, frequency_tier=1),
    CMEntry(70, "1^°NSAbsep/o+",  "ESCOGER-1",        None,
            C, X, X, X, [1], OPP, E,
            non_selected_above=True, spread=SPREAD, frequency_tier=2),
    CMEntry(71, "1+°NSAbsep/o+c-","EXPLICAR",         None,
            C, X, X, X, [1], OPP, E,
            non_selected_above=True, spread=SPREAD, frequency_tier=2),
    CMEntry(72, "1^°NSAb-/o+c+",  "ESCOGER-2",        "[F̂]",
            C, X, X, X, [1], OPP, E,
            non_selected_above=True, thumb_contact=True, frequency_tier=2),
    CMEntry(73, "1+°NSAbsep/o+d°c+","YOGA",           None,
            C, X, X, X, [1], OPP, E,
            non_selected_above=True, spread=SPREAD, thumb_contact=True, frequency_tier=3,
            distal_override="d°"),
    CMEntry(74, "1^°NSAb/o^c+y-", "LETRA-T-VAR",      "[T']",
            C, X, X, X, [1], OPP, B,
            non_selected_above=True, thumb_contact=True, frequency_tier=2),

    # ── GROUP E: Pinky, Special, & Combined — CMs #75-101 ───────────────────

    CMEntry(75, "14+/o-",         "CL:VEHÍCULO",      "[Y']",
            E, X, X, E, [1,4], OPP, X, frequency_tier=1),
    CMEntry(76, "14+sep/o-",      "CARACOL",          None,
            E, X, X, E, [1,4], OPP, X, spread=SPREAD, frequency_tier=3),
    CMEntry(77, "14+/a+",         "HORA-RELOJ",       None,
            E, X, X, E, [1,4], PAR, E, frequency_tier=2),
    CMEntry(78, "14+sep/o+",      "AVIÓN",            None,
            E, X, X, E, [1,4], OPP, E, spread=SPREAD, frequency_tier=2),
    CMEntry(79, "14+sep/a+",      "I-LOVE",           "[Y\"]",
            E, X, X, E, [1,4], PAR, E, spread=SPREAD, frequency_tier=2),
    CMEntry(80, "4+/o-",          "LETRA-I",          "[I]",
            X, X, X, E, [4], OPP, X, frequency_tier=1),
    CMEntry(81, "4+sep/a+",       "LETRA-Y",          "[Y]",
            X, X, X, E, [4], PAR, E, spread=SPREAD, frequency_tier=1),
    CMEntry(82, "4\"°/o-",        "INVESTIGAR-2",     None,
            X, X, X, C, [4], OPP, X, frequency_tier=3),
    CMEntry(83, "4+/o^c+y-",      "TIJUANA",          None,
            X, X, X, E, [4], OPP, B, thumb_contact=True, frequency_tier=3),
    CMEntry(84, "2^°NSAb-/o+d-c+","SORPRENDER",       None,
            X, C, X, X, [2], OPP, E,
            non_selected_above=True, thumb_contact=True, frequency_tier=3,
            distal_override="d-"),
    CMEntry(85, "2^°NSAb-/o+d-c+y-","DETESTAR",       None,
            X, C, X, X, [2], OPP, E,
            non_selected_above=True, thumb_contact=True, frequency_tier=3,
            distal_override="d-"),
    CMEntry(86, "2^°NSAb-/a+",    "GRACIAS",          None,
            X, C, X, X, [2], PAR, E,
            non_selected_above=True, frequency_tier=2),
    CMEntry(87, "2^°NSAbsep/a+",  "SENTIR",           None,
            X, C, X, X, [2], PAR, E,
            non_selected_above=True, spread=SPREAD, frequency_tier=2),
    CMEntry(88, "12+crz 4+sep/o-d-c+y-", "IRO",      None,
            E, E, X, E, [1,2,4], OPP, X,
            interaction=FingerInteraction.CROSSED, thumb_contact=True, frequency_tier=4,
            distal_override="d-",
            notes="Complex: 12 crossed + 4 separated, proper name only"),
    CMEntry(89, "124+sep/o-d-c+y-","VIPS",            None,
            E, E, X, E, [1,2,4], OPP, X,
            spread=SPREAD, thumb_contact=True, frequency_tier=4,
            distal_override="d-",
            notes="Proper name only"),
    CMEntry(90, "1\"°4+/a+",      "RARO-2",           None,
            C, X, X, E, [1,4], PAR, E, frequency_tier=3),
    CMEntry(91, "23^°NSAb-/o+c+", "VACA",             None,
            X, C, C, X, [2,3], OPP, E,
            non_selected_above=True, thumb_contact=True, frequency_tier=3),
    CMEntry(92, "12+apil/o-",     "HORMIGA-2",        None,
            E, E, X, X, [1,2], OPP, X,
            interaction=FingerInteraction.STACKED, frequency_tier=3),
    CMEntry(93, "12^/a+",         "HERMOSILLO-2",     None,
            B, B, X, X, [1,2], PAR, E, frequency_tier=3),
    CMEntry(94, "1^2+/o+c-",      "NÚM.30-ANT-1",    None,
            B, E, X, X, [1,2], OPP, E, frequency_tier=4,
            notes="Mixed flexion: index bent, middle extended"),
    CMEntry(95, "1+°2+/o+c+",     "NÚM.30-ANT-2",    None,
            C, E, X, X, [1,2], OPP, E, thumb_contact=True, frequency_tier=4,
            notes="Mixed flexion: index curved, middle extended"),
    CMEntry(96, "1234\"°/a+",     "MORADO",           None,
            C, C, C, C, [1,2,3,4], PAR, E, frequency_tier=3),
    CMEntry(97, "12\"°/a+",       "GRÚA",             None,
            C, C, X, X, [1,2], PAR, E, frequency_tier=3),
    CMEntry(98, "1\"°/a+",        "DISPARAR-2",       None,
            C, X, X, X, [1], PAR, E, frequency_tier=4),
    CMEntry(99, "1\"°-NSAb+/a+",  "TIERRA-2",         None,
            C, X, X, X, [1], PAR, E,
            non_selected_above=True, frequency_tier=4,
            notes="Single example in corpus"),
    CMEntry(100,"1^/o^c+",        "DESPUÉS-2",        None,
            B, X, X, X, [1], OPP, B, thumb_contact=True, frequency_tier=4,
            notes="Single example in corpus"),
    CMEntry(101,"4+sepNSAb/a+",   "IMPRENTA-2",       None,
            X, X, X, E, [4], PAR, E,
            non_selected_above=True, spread=SPREAD, frequency_tier=4,
            notes="Single example in corpus"),
]

# Fix: dataclass doesn't use `tier :=` walrus — assign frequency_tier properly
# The walrus operator above is a syntax trick that won't work in dataclass init.
# Let's use a proper constructor approach below.

# ═══════════════════════════════════════════════════════════════════════════════
# Lookup helpers
# ═══════════════════════════════════════════════════════════════════════════════

def get_cm(cm_id: int) -> CMEntry:
    """Get a CM by its ID (1-101)."""
    for cm in CM_INVENTORY:
        if cm.cm_id == cm_id:
            return cm
    raise KeyError(f"CM #{cm_id} not found")


def get_cms_by_tier(tier: int) -> list[CMEntry]:
    """Get all CMs in a given frequency tier."""
    return [cm for cm in CM_INVENTORY if cm.frequency_tier == tier]


def get_cm_by_code(alpha_code: str) -> CMEntry:
    """Get a CM by its alphabetic code, e.g. '[A]', '[V]'."""
    for cm in CM_INVENTORY:
        if cm.alpha_code == alpha_code:
            return cm
    raise KeyError(f"CM code '{alpha_code}' not found")


def get_cm_stats() -> dict:
    """Get summary statistics of the inventory."""
    tiers = {1: 0, 2: 0, 3: 0, 4: 0}
    for cm in CM_INVENTORY:
        tiers[cm.frequency_tier] += 1
    return {
        "total": len(CM_INVENTORY),
        "tier_1_high": tiers[1],
        "tier_2_medium": tiers[2],
        "tier_3_low": tiers[3],
        "tier_4_rare": tiers[4],
        "with_alpha_code": sum(1 for cm in CM_INVENTORY if cm.alpha_code),
        "with_thumb_contact": sum(1 for cm in CM_INVENTORY if cm.thumb_contact),
        "with_nsab": sum(1 for cm in CM_INVENTORY if cm.non_selected_above),
    }
