from dataclasses import dataclass
from typing import List, Tuple
from agents.utils import haversine

@dataclass
class RoutePlan:
    order: List[Tuple[float, float]]
    total_km: float

class LogisticsAgent:
    """Assigns a vehicle and builds a simple nearest-neighbor multi-stop route."""
    def __init__(self):
        pass

    def nearest_neighbor(self, start_lat, start_lon, stops: List[Tuple[float,float]]) -> RoutePlan:
        remaining = stops[:]
        order = []
        cur = (start_lat, start_lon)
        total = 0.0
        while remaining:
            nxt = min(remaining, key=lambda p: haversine(cur[0], cur[1], p[0], p[1]))
            total += haversine(cur[0], cur[1], nxt[0], nxt[1])
            order.append(nxt)
            remaining.remove(nxt)
            cur = nxt
        return RoutePlan(order=order, total_km=total)
