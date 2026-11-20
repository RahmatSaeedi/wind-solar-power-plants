"""Site screening and micro-siting (chapter 14): a raster grid in a local
projected frame (x east, y north, metres), slope and aspect, polygons and
buffers, a teaching speed-up over low hills, cable trees, least-cost
corridors, cut and fill of a level pad, and the geometric shadow-flicker
hours of a dwelling.

Teaching implementation: real projects work in a surveyed projected
coordinate system with a GIS, use flow models validated for the terrain,
and follow the setbacks, noise and flicker rules of the authority that
permits the project (chapters 55-57); none are quoted here.
"""
from __future__ import annotations

import heapq
import math
from dataclasses import dataclass

import numpy as np
from scipy import ndimage


# ------------------------------------------------------------ grid
@dataclass(frozen=True)
class Grid:
    """Regular raster: cell centres x0 + (i + 0.5) cell, y0 + (j + 0.5) cell;
    arrays are indexed [j, i] (row = north index, column = east index)."""
    x0: float
    y0: float
    cell: float
    nx: int
    ny: int

    def mesh(self) -> tuple[np.ndarray, np.ndarray]:
        x = self.x0 + (np.arange(self.nx) + 0.5) * self.cell
        y = self.y0 + (np.arange(self.ny) + 0.5) * self.cell
        return np.meshgrid(x, y)

    def index(self, x: float, y: float) -> tuple[int, int]:
        i = int((x - self.x0) // self.cell)
        j = int((y - self.y0) // self.cell)
        return min(max(j, 0), self.ny - 1), min(max(i, 0), self.nx - 1)

    def sample(self, field: np.ndarray, x, y):
        """Nearest-cell value of a raster at points."""
        x, y = np.atleast_1d(x), np.atleast_1d(y)
        out = np.array([field[self.index(a, b)] for a, b in zip(x, y)])
        return out

    def interp(self, field: np.ndarray, x, y):
        """Bilinear value of a raster at points (use it for profiles along a
        line: nearest-cell values jump at cell edges and fake steep grades)."""
        x, y = np.atleast_1d(np.asarray(x, float)), np.atleast_1d(np.asarray(y, float))
        ci = (x - self.x0) / self.cell - 0.5
        cj = (y - self.y0) / self.cell - 0.5
        return ndimage.map_coordinates(field, [cj, ci], order=1, mode="nearest")


# [start: slope]
def slope_percent(z: np.ndarray, cell: float) -> np.ndarray:
    """Steepest slope of a terrain raster in per cent (rise over run)."""
    dz_dy, dz_dx = np.gradient(z, cell)
    return 100.0 * np.hypot(dz_dx, dz_dy)


def aspect_deg(z: np.ndarray, cell: float) -> np.ndarray:
    """Direction the slope faces (downhill), degrees clockwise from north."""
    dz_dy, dz_dx = np.gradient(z, cell)
    return (np.degrees(np.arctan2(-dz_dx, -dz_dy))) % 360.0
# [end: slope]


# ------------------------------------------------------------ geometry
def polygon_area(poly) -> float:
    """Area of a simple polygon [(x, y), ...] by the shoelace formula."""
    p = np.asarray(poly, float)
    x, y = p[:, 0], p[:, 1]
    return 0.5 * abs(float(np.dot(x, np.roll(y, -1)) - np.dot(y, np.roll(x, -1))))


def in_polygon(x, y, poly) -> np.ndarray:
    """Ray-casting test of points (arrays) inside a polygon."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    p = np.asarray(poly, float)
    inside = np.zeros(np.broadcast(x, y).shape, bool)
    n = len(p)
    for k in range(n):
        (xa, ya), (xb, yb) = p[k], p[(k + 1) % n]
        cross = (ya > y) != (yb > y)
        with np.errstate(divide="ignore", invalid="ignore"):
            xi = xa + (y - ya) * (xb - xa) / (yb - ya)
        inside ^= cross & (x < xi)
    return inside


def distance_to(x, y, points) -> np.ndarray:
    """Distance from each (x, y) to the nearest of a set of points."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    d = np.full(np.broadcast(x, y).shape, np.inf)
    for px, py in points:
        d = np.minimum(d, np.hypot(x - px, y - py))
    return d


def distance_to_segments(x, y, polyline) -> np.ndarray:
    """Distance from points to the nearest segment of a polyline."""
    x, y = np.asarray(x, float), np.asarray(y, float)
    p = np.asarray(polyline, float)
    d = np.full(np.broadcast(x, y).shape, np.inf)
    for (xa, ya), (xb, yb) in zip(p[:-1], p[1:]):
        vx, vy = xb - xa, yb - ya
        t = np.clip(((x - xa) * vx + (y - ya) * vy) / (vx * vx + vy * vy), 0, 1)
        d = np.minimum(d, np.hypot(x - xa - t * vx, y - ya - t * vy))
    return d


# ------------------------------------------------------------ flow
# [start: speedup]
def hill_speedup(z: np.ndarray, cell: float, length: float,
                 factor: float = 2.0, limit: float = 0.3) -> np.ndarray:
    """Teaching speed-up over low, smooth hills: the fractional change of
    the wind speed is about factor x (local height above the surroundings)
    / (horizontal length scale). Valid only for gentle slopes without flow
    separation; real projects use a validated flow model (chapter 14)."""
    n = max(int(round(length / cell)), 1)
    around = ndimage.uniform_filter(z, size=2 * n + 1, mode="nearest")
    return np.clip(factor * (z - around) / length, -limit, limit)
# [end: speedup]


# ------------------------------------------------------------ networks
# [start: mst]
def minimum_spanning_tree(points) -> tuple[list[tuple[int, int]], float]:
    """Prim's algorithm on straight-line distances: the shortest network
    that connects every point (a lower bound for a cable or road)."""
    p = np.asarray(points, float)
    n = len(p)
    d = np.hypot(p[:, None, 0] - p[None, :, 0], p[:, None, 1] - p[None, :, 1])
    used = np.zeros(n, bool)
    used[0] = True
    best = d[0].copy()
    parent = np.zeros(n, int)
    edges, total = [], 0.0
    for _ in range(n - 1):
        cand = np.where(used, np.inf, best)
        k = int(np.argmin(cand))
        edges.append((int(parent[k]), k))
        total += float(cand[k])
        used[k] = True
        closer = d[k] < best
        best = np.where(closer, d[k], best)
        parent = np.where(closer, k, parent)
    return edges, total
# [end: mst]


def radial_strings(points, root, per_string: int) -> tuple[list[list[int]], float]:
    """Radial collector strings: turbines sorted by bearing from the root
    (substation), cut into groups of per_string, each group chained from
    the root by nearest neighbour. Returns the strings and total length."""
    p = np.asarray(points, float)
    r = np.asarray(root, float)
    ang = np.degrees(np.arctan2(p[:, 0] - r[0], p[:, 1] - r[1])) % 360
    order = list(np.argsort(ang))
    strings, total = [], 0.0
    for k in range(0, len(order), per_string):
        group = order[k:k + per_string]
        pos, chain = r, []
        left = list(group)
        while left:
            j = min(left, key=lambda m: math.hypot(*(p[m] - pos)))
            total += math.hypot(*(p[j] - pos))
            pos = p[j]
            chain.append(int(j))
            left.remove(j)
        strings.append(chain)
    return strings, total


# [start: lcp]
def least_cost_path(cost: np.ndarray, start: tuple[int, int],
                    end: tuple[int, int], cell: float):
    """Dijkstra on the 8-neighbour raster: the cost of a step is the mean
    cost of the two cells times the step length. Returns the path (list of
    [j, i]) and its accumulated cost; cells with infinite cost are no-go."""
    ny, nx = cost.shape
    steps = [(dj, di, cell * math.hypot(dj, di)) for dj in (-1, 0, 1)
             for di in (-1, 0, 1) if dj or di]
    acc = np.full(cost.shape, np.inf)
    prev = {}
    acc[start] = 0.0
    heap = [(0.0, start)]
    while heap:
        c, (j, i) = heapq.heappop(heap)
        if (j, i) == end:
            break
        if c > acc[j, i]:
            continue
        for dj, di, length in steps:
            a, b = j + dj, i + di
            if 0 <= a < ny and 0 <= b < nx and np.isfinite(cost[a, b]):
                nc = c + 0.5 * (cost[j, i] + cost[a, b]) * length
                if nc < acc[a, b]:
                    acc[a, b] = nc
                    prev[(a, b)] = (j, i)
                    heapq.heappush(heap, (nc, (a, b)))
    path, node = [end], end
    while node != start:
        node = prev[node]
        path.append(node)
    return path[::-1], float(acc[end])
# [end: lcp]


def cost_distance(cost: np.ndarray, start: tuple[int, int], cell: float) -> np.ndarray:
    """Accumulated least cost from one cell to every cell (Dijkstra without
    a target). Two such rasters, from each end of a route, add up to the
    cost of the best route through each cell: cells within a few per cent
    of the minimum form the corridor of near-optimal routes."""
    ny, nx = cost.shape
    steps = [(dj, di, cell * math.hypot(dj, di)) for dj in (-1, 0, 1)
             for di in (-1, 0, 1) if dj or di]
    acc = np.full(cost.shape, np.inf)
    acc[start] = 0.0
    heap = [(0.0, start)]
    while heap:
        c, (j, i) = heapq.heappop(heap)
        if c > acc[j, i]:
            continue
        for dj, di, length in steps:
            a, b = j + dj, i + di
            if 0 <= a < ny and 0 <= b < nx and np.isfinite(cost[a, b]):
                nc = c + 0.5 * (cost[j, i] + cost[a, b]) * length
                if nc < acc[a, b]:
                    acc[a, b] = nc
                    heapq.heappush(heap, (nc, (a, b)))
    return acc


def path_length(path, cell: float) -> float:
    """Length of a raster path (list of [j, i]) in metres."""
    p = np.asarray(path, float)
    return float(cell * np.hypot(*np.diff(p, axis=0).T).sum())


# ------------------------------------------------------------ earthworks
def cut_fill(z_patch: np.ndarray, cell: float, level: float | None = None):
    """Cut and fill volumes (m3) to make a raster patch flat at a level
    (default: the mean, which balances them)."""
    lv = float(np.mean(z_patch)) if level is None else level
    dz = z_patch - lv
    a = cell * cell
    return float(dz[dz > 0].sum() * a), float(-dz[dz < 0].sum() * a), lv


# ------------------------------------------------------------ flicker
# [start: flicker]
def flicker_minutes(house, turbines, hub: float, radius: float, sun_el, sun_az,
                    step_min: float, z_house: float = 0.0, z_turb=None,
                    min_el: float = 3.0, max_dist: float = 2000.0) -> np.ndarray:
    """Geometric shadow-flicker minutes per sun position (worst case: rotor
    always turning and facing the sun, sky always clear): the rotor is a
    sphere of the rotor radius around the hub; the house is shaded when the
    line to the sun passes through it."""
    el, az = np.radians(np.asarray(sun_el)), np.radians(np.asarray(sun_az))
    s = np.stack([np.cos(el) * np.sin(az), np.cos(el) * np.cos(az), np.sin(el)])
    hit = np.zeros(el.shape, bool)
    zt = np.zeros(len(turbines)) if z_turb is None else np.asarray(z_turb, float)
    for (tx, ty), zb in zip(turbines, zt):
        h = np.array([tx - house[0], ty - house[1], zb + hub - z_house])
        if math.hypot(h[0], h[1]) > max_dist:
            continue
        along = h @ s
        perp = np.sqrt(np.maximum(h @ h - along ** 2, 0.0))
        hit |= (along > 0) & (perp < radius)
    return np.where(hit & (np.degrees(el) > min_el), step_min, 0.0)
# [end: flicker]
