from dataclasses import dataclass
from typing import Tuple
from agents.utils import haversine

@dataclass
class MatchScore:
    score: float
    reason: str

class MatchingAgent:
    """Computes compatibility score between a donation and a request."""
    def __init__(self):
        pass

    def score(self, donation, request) -> MatchScore:
        # base score from food preference
        food_score = 1.0 if (donation.is_veg or (not donation.is_veg and not request.prefers_veg)) else 0.3
        # quantity fit
        qty_ratio = min(1.0, donation.quantity_meals / max(1, request.need_meals))
        # distance penalty
        dist_km = haversine(donation.lat, donation.lon, request.lat, request.lon)
        dist_score = max(0.0, 1.0 - (dist_km / 10.0))  # 0 at 10+ km
        # freshness: if donation expires soon, prioritize
        time_score = 1.0
        s = 0.4*food_score + 0.3*qty_ratio + 0.2*dist_score + 0.1*time_score
        return MatchScore(score=s, reason=f"food={food_score:.2f}, qty={qty_ratio:.2f}, dist={dist_km:.1f}km")
