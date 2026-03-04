"""
LSM-PN Phonological Enums
Canonical value types for the LSM Phonological Notation system.
"""
from enum import Enum


# ── Hand Configuration (CM) ──────────────────────────────────────────────────

class FlexionLevel(str, Enum):
    """4-level finger flexion discretization (§4.4.1 tech doc).
    Maps to proportional joint angles: MCP, PIP, DIP."""
    EXTENDED = "EXTENDED"    # 0%   — fingers straight
    CURVED   = "CURVED"      # 33%  — slight bend (redondeado °)
    BENT     = "BENT"        # 66%  — significant bend (aplanado ^)
    CLOSED   = "CLOSED"      # 100% — fully closed (cerrado -)


class ThumbOpposition(str, Enum):
    """Thumb rotation relative to finger plane."""
    OPPOSED  = "OPPOSED"     # Cruz Aldrete: 'o' — thumb faces fingers
    PARALLEL = "PARALLEL"    # Cruz Aldrete: 'a' — thumb aligned with fingers
    CROSSED  = "CROSSED"     # thumb crosses over fingers


class FingerSpread(str, Enum):
    """Lateral displacement between selected fingers."""
    CLOSED  = "CLOSED"       # fingers together
    NEUTRAL = "NEUTRAL"      # default position
    SPREAD  = "SPREAD"       # Cruz Aldrete: 'sep' — fingers spread apart


class FingerInteraction(str, Enum):
    """Special finger arrangement modifiers."""
    NONE     = "NONE"
    SPREAD   = "SPREAD"      # sep — separated
    STACKED  = "STACKED"     # apil — one finger on top of another
    CROSSED  = "CROSSED"     # crz — fingers crossed


class FingerID(str, Enum):
    """Finger identifiers. Cruz Aldrete: 1=index, 2=middle, 3=ring, 4=pinky."""
    THUMB  = "THUMB"
    INDEX  = "INDEX"    # D1 / finger 1
    MIDDLE = "MIDDLE"   # D2 / finger 2
    RING   = "RING"     # D3 / finger 3
    PINKY  = "PINKY"    # D4 / finger 4


# ── Location (UB) ────────────────────────────────────────────────────────────

class BodyRegion(str, Enum):
    """Major body regions for location classification."""
    HEAD          = "HEAD"
    FACE          = "FACE"
    NECK          = "NECK"
    TRUNK         = "TRUNK"
    ARM           = "ARM"
    FOREARM       = "FOREARM"
    HAND          = "HAND"
    NEUTRAL_SPACE = "NEUTRAL_SPACE"


class ContactType(str, Enum):
    """Proximity/contact between hand surface and location."""
    TOUCHING = "TOUCHING"    # Cruz Aldrete: Cont
    GRASPED  = "GRASPED"     # Cruz Aldrete: Prensado
    NEAR     = "NEAR"        # Cruz Aldrete: Prox
    MEDIAL   = "MEDIAL"      # Cruz Aldrete: Enfr (medio)
    DISTANT  = "DISTANT"     # Cruz Aldrete: Dist
    BRUSHING = "BRUSHING"    # Cruz Aldrete: Roz (rozando)


class Laterality(str, Enum):
    """Side relative to dominant hand."""
    IPSILATERAL   = "IPSILATERAL"    # same side as active hand
    CONTRALATERAL = "CONTRALATERAL"  # opposite side (Cruz Aldrete: X)
    MIDLINE       = "MIDLINE"        # center


# ── Movement (MV) ────────────────────────────────────────────────────────────

class ContourMovement(str, Enum):
    """5 contour/path movements (§4.1.2 Cruz Aldrete)."""
    STRAIGHT = "STRAIGHT"    # lin — linear
    ARC      = "ARC"         # arc — curved arc
    CIRCLE   = "CIRCLE"      # circ — circular
    ZIGZAG   = "ZIGZAG"      # zig — alternating direction
    SEVEN    = "SEVEN"       # 7 — acute angle path


class LocalMovement(str, Enum):
    """11 local/in-place movements (§4.1.3 Cruz Aldrete)."""
    WIGGLE      = "WIGGLE"       # ond — ondulante: sequential finger wave
    CIRCULAR    = "CIRCULAR"     # cir — circular wrist rotation
    TWIST       = "TWIST"        # rot — rotación: pronation/supination
    SCRATCH     = "SCRATCH"      # rsc — rascamiento: repeated finger flexion
    NOD         = "NOD"          # cab — cabeceo: finger bending at MCP
    OSCILLATE   = "OSCILLATE"    # osc — oscilante: alternating between 2 CMs
    RELEASE     = "RELEASE"      # solt — soltura: sudden opening
    FLATTEN     = "FLATTEN"      # apl — aplanado: closing to bent
    PROGRESSIVE = "PROGRESSIVE"  # prog — progressive sequential closure
    VIBRATE     = "VIBRATE"      # vib — vibrante: trembling
    RUB         = "RUB"          # frot — frotación: thumb rubs fingertips


class MovementPlane(str, Enum):
    """Spatial plane on which contour movement occurs (§4.1.5)."""
    HORIZONTAL = "HORIZONTAL"  # PH — parallel to floor
    VERTICAL   = "VERTICAL"    # PV — perpendicular, facing signer
    SAGITTAL   = "SAGITTAL"    # PS — perpendicular, side-facing
    OBLIQUE    = "OBLIQUE"


# ── Orientation (OR / DI) ────────────────────────────────────────────────────

class PalmFacing(str, Enum):
    """Direction the palm faces (orientation component)."""
    UP       = "UP"
    DOWN     = "DOWN"
    FORWARD  = "FORWARD"
    BACK     = "BACK"
    LEFT     = "LEFT"
    RIGHT    = "RIGHT"
    NEUTRAL  = "NEUTRAL"


class FingerPointing(str, Enum):
    """Direction the extended fingers point (direction component)."""
    UP       = "UP"
    DOWN     = "DOWN"
    FORWARD  = "FORWARD"
    BACK     = "BACK"
    LEFT     = "LEFT"
    RIGHT    = "RIGHT"
    NEUTRAL  = "NEUTRAL"


# ── Segmental / Timing ───────────────────────────────────────────────────────

class SegmentType(str, Enum):
    """Segment types in the sequential model (Liddell & Johnson 1989)."""
    MOVEMENT  = "M"   # Dynamic segment with trajectory
    DETENTION = "D"   # Static hold
    TRANSITION = "T"  # Transitional segment


class Phase(str, Enum):
    """PSHR timing phases for sign production."""
    PREPARATION = "PREPARATION"  # P — hands move from rest to initial position
    STROKE      = "STROKE"       # S — meaningful movement
    HOLD        = "HOLD"         # H — final position maintained
    RETRACTION  = "RETRACTION"   # R — hands return to rest


# ── Non-Manual Features (RNM) ────────────────────────────────────────────────

class EyebrowPosition(str, Enum):
    NEUTRAL = "NEUTRAL"
    RAISED  = "RAISED"
    FURROWED = "FURROWED"   # Cruz Aldrete: CinFruncido


class MouthShape(str, Enum):
    NEUTRAL    = "NEUTRAL"
    OPEN       = "OPEN"
    CLOSED     = "CLOSED"
    ROUNDED    = "ROUNDED"
    STRETCHED  = "STRETCHED"  # Cruz Aldrete: LabDistendidos


class HeadMovement(str, Enum):
    NONE       = "NONE"
    NOD        = "NOD"        # CaAd — cabeza adelante
    SHAKE      = "SHAKE"
    TILT_LEFT  = "TILT_LEFT"  # CaLat
    TILT_RIGHT = "TILT_RIGHT"
    TILT_BACK  = "TILT_BACK"  # CaAt — cabeza atrás
    TILT_DOWN  = "TILT_DOWN"  # CaAg — cabeza agachada
