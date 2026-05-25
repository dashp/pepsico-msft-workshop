"""Generate small, realistic sample CSVs for Lab 01.

Run once from the workshop repo root:
    python workshop/Allfiles/lab01/generate.py

Produces three files alongside this script:
    sales.csv         (~10,000 rows)
    dim_store.csv     (~50 rows)
    dim_product.csv   (~25 rows)

Data is fully synthetic. No real PepsiCo data is used.
"""
from __future__ import annotations

import csv
import datetime as dt
import pathlib
import random

HERE = pathlib.Path(__file__).parent
random.seed(42)

# --- dim_product -------------------------------------------------------------

PRODUCTS = [
    # category, sub_category, name, list_price
    ("Beverages", "Sports Drinks",      "Gatorade Frost 28oz",        2.49),
    ("Beverages", "Sports Drinks",      "Gatorade Cool Blue 28oz",    2.49),
    ("Beverages", "Sports Drinks",      "Gatorade Glacier Freeze 28oz", 2.49),
    ("Beverages", "Sports Drinks",      "Gatorade Zero Lemon-Lime",   2.49),
    ("Beverages", "Energy",             "Mountain Dew Kickstart",     2.29),
    ("Beverages", "Energy",             "Rockstar Original",          2.99),
    ("Beverages", "Carbonated",         "Pepsi 20oz",                 1.99),
    ("Beverages", "Carbonated",         "Pepsi Zero 20oz",            1.99),
    ("Beverages", "Carbonated",         "Mountain Dew 20oz",          1.99),
    ("Beverages", "Carbonated",         "Mtn Dew Code Red 20oz",      1.99),
    ("Beverages", "Water",              "Aquafina 20oz",              1.59),
    ("Beverages", "Water",              "LIFEWTR 23.7oz",             2.49),
    ("Beverages", "Tea & Coffee",       "Lipton Pure Leaf Sweet Tea", 2.79),
    ("Beverages", "Tea & Coffee",       "Starbucks Frappuccino",      3.49),
    ("Snacks",    "Salty",              "Lay's Classic 2.625oz",      1.99),
    ("Snacks",    "Salty",              "Doritos Nacho Cheese 2.75oz",1.99),
    ("Snacks",    "Salty",              "Cheetos Crunchy 2oz",        1.79),
    ("Snacks",    "Salty",              "Ruffles Cheddar Sour Cream", 1.99),
    ("Snacks",    "Salty",              "SunChips Harvest Cheddar",   1.99),
    ("Snacks",    "Tortilla",           "Tostitos Scoops 10oz",       4.49),
    ("Snacks",    "Nuts & Seeds",       "Frito-Lay Mixed Nuts",       4.99),
    ("Snacks",    "Bars",               "Quaker Chewy Granola Bar",   0.99),
    ("Snacks",    "Bars",               "Gatorade Recover Whey Bar",  2.49),
    ("Breakfast", "Cereal",             "Quaker Oats Old Fashioned",  4.99),
    ("Breakfast", "Cereal",             "Cap'n Crunch Original",      3.99),
]


def write_dim_product(path: pathlib.Path) -> list[str]:
    ids: list[str] = []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["product_id", "product_name", "category", "sub_category", "list_price"])
        for i, (cat, sub, name, price) in enumerate(PRODUCTS, start=1):
            pid = f"P{i:03d}"
            ids.append(pid)
            w.writerow([pid, name, cat, sub, price])
    return ids


# --- dim_store ---------------------------------------------------------------

STORES = [
    # store_name, city, state, region
    ("HEB-Austin-South",       "Austin",        "TX", "South Central"),
    ("HEB-Austin-North",       "Austin",        "TX", "South Central"),
    ("HEB-Houston-Galleria",   "Houston",       "TX", "South Central"),
    ("HEB-Dallas-Uptown",      "Dallas",        "TX", "South Central"),
    ("HEB-San-Antonio-Center", "San Antonio",   "TX", "South Central"),
    ("HEB-El-Paso",            "El Paso",       "TX", "South Central"),
    ("Walmart-Plano-Legacy",   "Plano",         "TX", "South Central"),
    ("Walmart-Frisco",         "Frisco",        "TX", "South Central"),
    ("Walmart-Arlington",      "Arlington",     "TX", "South Central"),
    ("Walmart-Fort-Worth",     "Fort Worth",    "TX", "South Central"),
    ("Kroger-Atlanta-Buckhead","Atlanta",       "GA", "Southeast"),
    ("Kroger-Atlanta-Midtown", "Atlanta",       "GA", "Southeast"),
    ("Publix-Tampa-Bay",       "Tampa",         "FL", "Southeast"),
    ("Publix-Orlando-Disney",  "Orlando",       "FL", "Southeast"),
    ("Publix-Miami-Beach",     "Miami",         "FL", "Southeast"),
    ("Wegmans-NYC-Brooklyn",   "Brooklyn",      "NY", "Northeast"),
    ("Wegmans-Boston-Fenway",  "Boston",        "MA", "Northeast"),
    ("Stop-Shop-Hartford",     "Hartford",      "CT", "Northeast"),
    ("Giant-Philadelphia",     "Philadelphia",  "PA", "Northeast"),
    ("ShopRite-Newark",        "Newark",        "NJ", "Northeast"),
    ("Meijer-Chicago-Loop",    "Chicago",       "IL", "Midwest"),
    ("Meijer-Detroit",         "Detroit",       "MI", "Midwest"),
    ("Hy-Vee-Des-Moines",      "Des Moines",    "IA", "Midwest"),
    ("Mariano-Milwaukee",      "Milwaukee",     "WI", "Midwest"),
    ("Cub-Minneapolis",        "Minneapolis",   "MN", "Midwest"),
    ("Safeway-Denver-LoDo",    "Denver",        "CO", "Mountain"),
    ("King-Soopers-Boulder",   "Boulder",       "CO", "Mountain"),
    ("Smith-Salt-Lake",        "Salt Lake City","UT", "Mountain"),
    ("Albertsons-Phoenix",     "Phoenix",       "AZ", "Mountain"),
    ("Bashas-Tucson",          "Tucson",        "AZ", "Mountain"),
    ("Safeway-Seattle-Capitol","Seattle",       "WA", "Pacific"),
    ("Fred-Meyer-Portland",    "Portland",      "OR", "Pacific"),
    ("Safeway-SF-Marina",      "San Francisco", "CA", "Pacific"),
    ("Ralphs-LA-Hollywood",    "Los Angeles",   "CA", "Pacific"),
    ("Ralphs-LA-Westwood",     "Los Angeles",   "CA", "Pacific"),
    ("Vons-San-Diego",         "San Diego",     "CA", "Pacific"),
    ("Vons-Sacramento",        "Sacramento",    "CA", "Pacific"),
    ("Walmart-Las-Vegas",      "Las Vegas",     "NV", "Mountain"),
    ("Walmart-Reno",           "Reno",          "NV", "Mountain"),
    ("Walmart-Albuquerque",    "Albuquerque",   "NM", "Mountain"),
    ("Walmart-OKC",            "Oklahoma City", "OK", "South Central"),
    ("Walmart-Tulsa",          "Tulsa",         "OK", "South Central"),
    ("Walmart-Little-Rock",    "Little Rock",   "AR", "South Central"),
    ("Walmart-Memphis",        "Memphis",       "TN", "Southeast"),
    ("Walmart-Nashville",      "Nashville",     "TN", "Southeast"),
    ("Walmart-Charlotte",      "Charlotte",     "NC", "Southeast"),
    ("Walmart-Raleigh",        "Raleigh",       "NC", "Southeast"),
    ("Walmart-Columbus",       "Columbus",      "OH", "Midwest"),
    ("Walmart-Indianapolis",   "Indianapolis",  "IN", "Midwest"),
    ("Walmart-Louisville",     "Louisville",    "KY", "Southeast"),
]


def write_dim_store(path: pathlib.Path) -> list[str]:
    ids: list[str] = []
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["store_id", "store_name", "city", "state", "region"])
        for i, (name, city, state, region) in enumerate(STORES, start=1):
            sid = f"S{i:03d}"
            ids.append(sid)
            w.writerow([sid, name, city, state, region])
    return ids


# --- sales -------------------------------------------------------------------

def write_sales(
    path: pathlib.Path, store_ids: list[str], product_ids: list[str]
) -> int:
    """~10k rows of daily sales across 180 days, with seasonal + weekly effect."""
    start = dt.date.today() - dt.timedelta(days=180)
    rows = 0
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["sale_date", "store_id", "product_id", "units_sold", "revenue"])
        for d in range(180):
            day = start + dt.timedelta(days=d)
            weekend_boost = 1.25 if day.weekday() >= 5 else 1.0
            # peak in summer for sports drinks
            month_factor = 1.0 + 0.3 * (1 if day.month in (6, 7, 8) else 0)
            for sid in random.sample(store_ids, k=random.randint(8, 15)):
                for pid in random.sample(product_ids, k=random.randint(3, 6)):
                    base = random.randint(2, 18)
                    units = max(1, int(base * weekend_boost * month_factor
                                       * random.uniform(0.7, 1.3)))
                    price = next(p[3] for p in zip(
                        [f"P{i:03d}" for i in range(1, len(PRODUCTS) + 1)],
                        *[[p] for p in PRODUCTS]
                    ) if p[0] == pid) if False else PRODUCTS[
                        int(pid[1:]) - 1
                    ][3]
                    revenue = round(units * price * random.uniform(0.92, 1.0), 2)
                    w.writerow([day.isoformat(), sid, pid, units, revenue])
                    rows += 1
    return rows


# --- main --------------------------------------------------------------------

def main() -> None:
    product_ids = write_dim_product(HERE / "dim_product.csv")
    store_ids = write_dim_store(HERE / "dim_store.csv")
    n = write_sales(HERE / "sales.csv", store_ids, product_ids)
    print(f"wrote dim_product.csv ({len(product_ids)} rows)")
    print(f"wrote dim_store.csv   ({len(store_ids)} rows)")
    print(f"wrote sales.csv       ({n:,} rows)")


if __name__ == "__main__":
    main()
