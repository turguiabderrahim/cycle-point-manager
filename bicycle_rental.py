"""
Bicycle Rental Point Management System
=======================================
Classes:
  - Bicycle : stores data about a single bicycle
  - Point   : represents a rental point with a list of bicycles

Features:
  - Load multiple rental points from separate .txt files
  - Count usable / unusable bicycles and their total values
  - Average age of usable and unusable bicycles
  - Find the rental point with the oldest bicycle
  - Count city bikes per rental point
"""

from datetime import date
import os
import sys


# ─────────────────────────────────────────────
# Data classes
# ─────────────────────────────────────────────

class Bicycle:
    """Describes a single bicycle at a rental point."""

    VALID_PURPOSES = {"sports", "city", "mountain", "touring", "hybrid"}

    def __init__(self, manufacturer: str, year: int, price: float, purpose: str):
        self.manufacturer = manufacturer.strip()
        self.year = int(year)
        self.price = float(price)
        self.purpose = purpose.strip().lower()

    def age(self) -> int:
        """Returns the age of the bicycle in full years."""
        return date.today().year - self.year

    def is_usable(self, max_age: int) -> bool:
        """Returns True if the bicycle is not older than max_age years."""
        return self.age() <= max_age

    def __repr__(self):
        return (f"Bicycle({self.manufacturer!r}, {self.year}, "
                f"€{self.price:.2f}, {self.purpose})")


class Point:
    """Describes a bicycle rental point."""

    def __init__(self, name: str, bicycles: list[Bicycle] | None = None):
        self.name = name.strip()
        self.bicycles: list[Bicycle] = bicycles if bicycles is not None else []

    # ── I/O ──────────────────────────────────

    @classmethod
    def from_file(cls, filepath: str) -> "Point":
        """
        Load a rental point from a text file.

        File format (first line = point name, remaining lines = bicycles):
            <Point Name>
            <manufacturer>,<year>,<price>,<purpose>
            ...
        """
        with open(filepath, encoding="utf-8") as f:
            lines = [ln.rstrip("\n") for ln in f if ln.strip()]

        if not lines:
            raise ValueError(f"File '{filepath}' is empty.")

        name = lines[0]
        bicycles: list[Bicycle] = []

        for lineno, line in enumerate(lines[1:], start=2):
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 4:
                print(f"  [WARNING] {filepath}:{lineno} – expected 4 fields, "
                      f"got {len(parts)}. Skipping: {line!r}")
                continue
            try:
                manufacturer, year, price, purpose = parts
                bicycles.append(Bicycle(manufacturer, int(year),
                                        float(price), purpose))
            except ValueError as exc:
                print(f"  [WARNING] {filepath}:{lineno} – {exc}. "
                      f"Skipping: {line!r}")

        return cls(name, bicycles)

    # ── Analytics ────────────────────────────

    def usable_bicycles(self, max_age: int) -> list[Bicycle]:
        return [b for b in self.bicycles if b.is_usable(max_age)]

    def unusable_bicycles(self, max_age: int) -> list[Bicycle]:
        return [b for b in self.bicycles if not b.is_usable(max_age)]

    @staticmethod
    def _stats(bikes: list[Bicycle]) -> dict:
        """Return count, total value, and average age for a list of bikes."""
        count = len(bikes)
        total_value = sum(b.price for b in bikes)
        avg_age = sum(b.age() for b in bikes) / count if count else 0.0
        return {"count": count, "total_value": total_value, "avg_age": avg_age}

    def report(self, max_age: int) -> dict:
        usable   = self.usable_bicycles(max_age)
        unusable = self.unusable_bicycles(max_age)
        return {
            "usable":   self._stats(usable),
            "unusable": self._stats(unusable),
        }

    def oldest_bicycle(self) -> Bicycle | None:
        """Returns the oldest bicycle at this point, or None if empty."""
        return min(self.bicycles, key=lambda b: b.year, default=None)

    def city_bike_count(self) -> int:
        return sum(1 for b in self.bicycles if b.purpose == "city")

    def __repr__(self):
        return f"Point({self.name!r}, {len(self.bicycles)} bikes)"


# ─────────────────────────────────────────────
# Multi-point analytics
# ─────────────────────────────────────────────

def point_with_oldest_bike(points: list[Point]) -> tuple[Point, Bicycle] | tuple[None, None]:
    """Returns (point, bicycle) for the oldest bicycle across all points."""
    best_point, best_bike = None, None
    for point in points:
        bike = point.oldest_bicycle()
        if bike and (best_bike is None or bike.year < best_bike.year):
            best_point, best_bike = point, bike
    return best_point, best_bike


def city_bikes_per_point(points: list[Point]) -> dict[str, int]:
    return {p.name: p.city_bike_count() for p in points}


# ─────────────────────────────────────────────
# Display helpers
# ─────────────────────────────────────────────

SEPARATOR = "─" * 60


def print_point_report(point: Point, max_age: int):
    stats = point.report(max_age)
    u  = stats["usable"]
    un = stats["unusable"]

    print(f"\n{'═' * 60}")
    print(f"  Rental Point : {point.name}")
    print(f"  Max usable age: {max_age} years  |  "
          f"Total bicycles: {len(point.bicycles)}")
    print(f"{'═' * 60}")

    print(f"\n  ✅  USABLE bicycles  (age ≤ {max_age} years)")
    print(f"  {SEPARATOR}")
    print(f"    Count      : {u['count']}")
    print(f"    Total value: €{u['total_value']:>10.2f}")
    print(f"    Average age: {u['avg_age']:>6.2f} years")

    print(f"\n  ❌  UNUSABLE bicycles (age > {max_age} years)")
    print(f"  {SEPARATOR}")
    print(f"    Count      : {un['count']}")
    print(f"    Total value: €{un['total_value']:>10.2f}")
    print(f"    Average age: {un['avg_age']:>6.2f} years")


def print_all_points_summary(points: list[Point], max_age: int):
    """Combined summary across all rental points."""
    all_usable   = [b for p in points for b in p.usable_bicycles(max_age)]
    all_unusable = [b for p in points for b in p.unusable_bicycles(max_age)]

    def stats(bikes):
        count = len(bikes)
        val   = sum(b.price for b in bikes)
        age   = sum(b.age() for b in bikes) / count if count else 0.0
        return count, val, age

    uc, uv, ua   = stats(all_usable)
    nc, nv, na   = stats(all_unusable)
    total        = uc + nc

    print(f"\n{'═' * 60}")
    print(f"  COMBINED SUMMARY – all {len(points)} rental point(s)")
    print(f"{'═' * 60}")
    print(f"    Total bicycles     : {total}")
    print(f"\n  ✅  Usable (age ≤ {max_age} years)")
    print(f"    Count              : {uc}")
    print(f"    Total value        : €{uv:.2f}")
    print(f"    Average age        : {ua:.2f} years")
    print(f"\n  ❌  Unusable (age > {max_age} years)")
    print(f"    Count              : {nc}")
    print(f"    Total value        : €{nv:.2f}")
    print(f"    Average age        : {na:.2f} years")

    # Oldest bike
    oldest_point, oldest_bike = point_with_oldest_bike(points)
    if oldest_bike:
        print(f"\n  🏆  Oldest bicycle")
        print(f"    Rental point : {oldest_point.name}")
        print(f"    Bicycle      : {oldest_bike.manufacturer} "
              f"({oldest_bike.year})  –  age {oldest_bike.age()} years")

    # City bikes
    print(f"\n  🚲  City bikes per rental point")
    for name, count in city_bikes_per_point(points).items():
        print(f"    {name:<30} : {count}")
    print()


# ─────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────

def get_data_files(args: list[str]) -> list[str]:
    """
    Resolve data files from command-line args or interactively.
    Falls back to auto-detecting point*.txt in the current directory.
    """
    if args:
        return args

    # Auto-detect pointN.txt files in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    detected = sorted(
        os.path.join(script_dir, f)
        for f in os.listdir(script_dir)
        if f.startswith("point") and f.endswith(".txt")
    )
    if detected:
        print("Auto-detected data files:")
        for p in detected:
            print(f"  {p}")
        return detected

    # Ask the user
    print("No data files detected. Enter file paths one per line "
          "(empty line to finish):")
    files = []
    while True:
        path = input("  File path: ").strip()
        if not path:
            break
        if os.path.isfile(path):
            files.append(path)
        else:
            print(f"  [ERROR] File not found: {path!r}")
    return files


def main():
    print("=" * 60)
    print("   BICYCLE RENTAL POINT MANAGEMENT SYSTEM")
    print("=" * 60)

    # ── Determine data files ──────────────────
    files = get_data_files(sys.argv[1:])
    if not files:
        print("[ERROR] No data files provided. Exiting.")
        sys.exit(1)

    # ── Ask for max usable age ────────────────
    while True:
        try:
            max_age = int(input("\nEnter maximum usable age (years): "))
            if max_age < 0:
                raise ValueError
            break
        except ValueError:
            print("  Please enter a non-negative integer.")

    # ── Load rental points ────────────────────
    points: list[Point] = []
    for filepath in files:
        try:
            point = Point.from_file(filepath)
            points.append(point)
            print(f"  Loaded: {point.name!r}  ({len(point.bicycles)} bicycles)")
        except (FileNotFoundError, ValueError) as exc:
            print(f"  [ERROR] Could not load {filepath!r}: {exc}")

    if not points:
        print("[ERROR] No rental points loaded. Exiting.")
        sys.exit(1)

    # ── Per-point reports ─────────────────────
    for point in points:
        print_point_report(point, max_age)

    # ── Combined summary ──────────────────────
    print_all_points_summary(points, max_age)


if __name__ == "__main__":
    main()
