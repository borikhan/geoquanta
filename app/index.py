from collections import defaultdict
from dataclasses import dataclass
from math import asin, cos, floor, radians, sin, sqrt
from threading import RLock


@dataclass(frozen=True)
class Point:
    id: str
    lat: float
    lon: float
    metadata: dict


def distance_km(a: Point, lat: float, lon: float) -> float:
    dlat, dlon = radians(lat - a.lat), radians(lon - a.lon)
    value = sin(dlat / 2) ** 2 + cos(radians(a.lat)) * cos(radians(lat)) * sin(dlon / 2) ** 2
    return 6371.0 * 2 * asin(sqrt(value))


class GeoIndex:
    def __init__(self, cell_degrees: float = 0.25):
        self.cell = cell_degrees
        self.cells: dict[tuple[int, int], list[Point]] = defaultdict(list)
        self.lock = RLock()

    def _key(self, lat: float, lon: float) -> tuple[int, int]:
        return floor(lat / self.cell), floor(lon / self.cell)

    def add(self, points: list[Point]) -> int:
        with self.lock:
            for point in points:
                if not (-90 <= point.lat <= 90 and -180 <= point.lon <= 180):
                    raise ValueError(f"invalid coordinates for {point.id}")
                self.cells[self._key(point.lat, point.lon)].append(point)
        return len(points)

    def nearest(self, lat: float, lon: float, radius_km: float, limit: int) -> list[tuple[Point, float]]:
        rings = max(1, int(radius_km / (self.cell * 80)) + 1)
        x, y = self._key(lat, lon)
        candidates: list[Point] = []
        with self.lock:
            for dx in range(-rings, rings + 1):
                for dy in range(-rings, rings + 1):
                    candidates.extend(self.cells.get((x + dx, y + dy), []))
        result = [(point, distance_km(point, lat, lon)) for point in candidates]
        return sorted((item for item in result if item[1] <= radius_km), key=lambda item: item[1])[:limit]
