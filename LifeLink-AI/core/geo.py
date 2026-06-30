"""Geospatial helpers — distance + travel-time estimates (no external API)."""
import math

# Average ambulance speed in dense urban traffic (km/h). Used to turn
# straight-line distance into a rough ETA. Intentionally conservative.
URBAN_AMBULANCE_KMH = 38.0
# Roads are never straight: inflate haversine distance to approximate real driving.
ROAD_FACTOR = 1.35
# Fixed dispatch + mobilization overhead (minutes) before the ambulance moves.
DISPATCH_OVERHEAD_MIN = 2.0


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two points in kilometers."""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlam = math.radians(lng2 - lng1)
    a = (math.sin(dphi / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin(dlam / 2) ** 2)
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def road_distance_km(lat1, lng1, lat2, lng2):
    """Approximate driving distance (haversine inflated by a road factor)."""
    return haversine_km(lat1, lng1, lat2, lng2) * ROAD_FACTOR


def eta_minutes(distance_km, kmh=URBAN_AMBULANCE_KMH):
    """Rough ambulance ETA in minutes for a given road distance."""
    if kmh <= 0:
        return None
    travel = distance_km / kmh * 60.0
    return int(round(travel + DISPATCH_OVERHEAD_MIN))
