from dataclasses import dataclass

@dataclass(frozen=True)
class UnitConfig:
    hp:         int
    speed:      float
    range:      int
    shoot_rate: int
    dmg:        int
    aoe:        int

UNIT_TYPES: dict[str, UnitConfig] = {
    "soldier": UnitConfig(hp=3,  speed=0.45, range=110, shoot_rate=70,  dmg=1, aoe=0),
    "archer":  UnitConfig(hp=2,  speed=0.30, range=200, shoot_rate=110, dmg=1, aoe=0),
    "cavalry": UnitConfig(hp=5,  speed=1.10, range=18,  shoot_rate=40,  dmg=2, aoe=0),
    "cannon":  UnitConfig(hp=6,  speed=0.12, range=160, shoot_rate=200, dmg=3, aoe=28),
}

WAVES: list[list[dict]] = [
    [{"type": "soldier", "count": 6}, {"type": "archer",  "count": 2}],
    [{"type": "soldier", "count": 5}, {"type": "archer",  "count": 3}, {"type": "cavalry", "count": 2}],
    [{"type": "soldier", "count": 4}, {"type": "cavalry", "count": 3}, {"type": "cannon",  "count": 1}],
    [{"type": "archer",  "count": 4}, {"type": "cavalry", "count": 3}, {"type": "cannon",  "count": 2}],
    [{"type": "soldier", "count": 6}, {"type": "archer",  "count": 3},
     {"type": "cavalry", "count": 3}, {"type": "cannon",  "count": 2}],
]