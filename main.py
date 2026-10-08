import json
import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Query, Path, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from database import get_db, init_db, row_to_bike_dict
from schemas import (
    BikeCreate,
    BikeUpdate,
    BikeResponse,
    CompareResponse,
    SpecComparison,
    FilterOptions
)

app = FastAPI(
    title="MotoCompare API",
    description="Backend API for MotoCompare motorcycle comparison and exploration platform",
    version="1.0.0"
)

# Enable CORS for cross-origin frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on application start
@app.on_event("startup")
def on_startup():
    init_db()

# --- BIKE CRUD & SEARCH ENDPOINTS ---

@app.get("/api/bikes", response_model=List[BikeResponse], tags=["Bikes"])
def list_bikes(
    search: Optional[str] = Query(None, description="Search term for model or brand"),
    brand: Optional[List[str]] = Query(None, description="Filter by brand (can specify multiple)"),
    type: Optional[List[str]] = Query(None, description="Filter by bike category/type"),
    max_price: Optional[float] = Query(None, description="Maximum ex-showroom price"),
    min_engine: Optional[float] = Query(None, description="Minimum engine displacement (cc)"),
    sort_by: Optional[str] = Query("default", description="Sort order: default, price-low, price-high, rating, power")
):
    """Retrieve motorcycles with optional search, filter criteria, and sorting."""
    conn = get_db()
    cursor = conn.cursor()

    query = "SELECT b.*, (f.bike_id IS NOT NULL) AS is_fav FROM bikes b LEFT JOIN favorites f ON b.id = f.bike_id WHERE 1=1"
    params = []

    if search:
        query += " AND (LOWER(b.brand) LIKE ? OR LOWER(b.model) LIKE ?)"
        term = f"%{search.lower().strip()}%"
        params.extend([term, term])

    if brand:
        placeholders = ",".join("?" for _ in brand)
        query += f" AND b.brand IN ({placeholders})"
        params.extend(brand)

    if type:
        placeholders = ",".join("?" for _ in type)
        query += f" AND b.type IN ({placeholders})"
        params.extend(type)

    if max_price is not None:
        query += " AND b.price <= ?"
        params.append(max_price)

    if min_engine is not None and min_engine > 0:
        query += " AND b.engine >= ?"
        params.append(min_engine)

    # Sorting
    if sort_by == "price-low":
        query += " ORDER BY b.price ASC"
    elif sort_by == "price-high":
        query += " ORDER BY b.price DESC"
    elif sort_by == "rating":
        query += " ORDER BY b.rating DESC"
    elif sort_by == "power":
        query += " ORDER BY b.power DESC"
    else:
        query += " ORDER BY b.rowid ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    results = []
    for r in rows:
        d = dict(r)
        is_fav = bool(d.pop("is_fav", 0))
        bike_data = row_to_bike_dict(sqlite3_row_mock(d))
        bike_data["isFavorite"] = is_fav
        results.append(bike_data)

    conn.close()
    return results

def sqlite3_row_mock(d):
    class MockRow(dict):
        pass
    return MockRow(d)

@app.get("/api/bikes/{bike_id}", response_model=BikeResponse, tags=["Bikes"])
def get_bike(bike_id: str = Path(..., description="The ID of the bike")):
    """Get complete specifications and details for a single motorcycle."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT b.*, (f.bike_id IS NOT NULL) AS is_fav 
        FROM bikes b 
        LEFT JOIN favorites f ON b.id = f.bike_id 
        WHERE b.id = ?
    """, (bike_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    d = dict(row)
    is_fav = bool(d.pop("is_fav", 0))
    bike = row_to_bike_dict(sqlite3_row_mock(d))
    bike["isFavorite"] = is_fav
    return bike

@app.post("/api/bikes", response_model=BikeResponse, status_code=status.HTTP_201_CREATED, tags=["Bikes"])
def create_bike(bike: BikeCreate):
    """Add a new motorcycle to the database."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id FROM bikes WHERE id = ?", (bike.id,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Bike with ID '{bike.id}' already exists.")

    price_disp = bike.priceDisplay or f"₹{(bike.price / 100000):.2f} Lakh"

    cursor.execute("""
        INSERT INTO bikes (
            id, brand, model, price, priceDisplay, engine, mileage, power, torque,
            topSpeed, weight, fuelCapacity, brakes, suspension, type, rating,
            image, pros_json, cons_json, features_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        bike.id,
        bike.brand,
        bike.model,
        bike.price,
        price_disp,
        bike.engine,
        bike.mileage,
        bike.power,
        bike.torque,
        bike.topSpeed,
        bike.weight,
        bike.fuelCapacity,
        bike.brakes,
        bike.suspension,
        bike.type,
        bike.rating or 4.5,
        bike.image or "",
        json.dumps(bike.pros),
        json.dumps(bike.cons),
        json.dumps(bike.features)
    ))
    conn.commit()
    conn.close()
    
    res = bike.dict()
    res["priceDisplay"] = price_disp
    res["isFavorite"] = False
    return res

@app.put("/api/bikes/{bike_id}", response_model=BikeResponse, tags=["Bikes"])
def update_bike(bike_id: str, updates: BikeUpdate):
    """Update bike specs and attributes."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bikes WHERE id = ?", (bike_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    existing = row_to_bike_dict(row)
    update_data = updates.dict(exclude_unset=True)

    for field, val in update_data.items():
        if field in ("pros", "cons", "features"):
            cursor.execute(f"UPDATE bikes SET {field}_json = ? WHERE id = ?", (json.dumps(val), bike_id))
        else:
            cursor.execute(f"UPDATE bikes SET {field} = ? WHERE id = ?", (val, bike_id))

    conn.commit()
    cursor.execute("""
        SELECT b.*, (f.bike_id IS NOT NULL) AS is_fav 
        FROM bikes b 
        LEFT JOIN favorites f ON b.id = f.bike_id 
        WHERE b.id = ?
    """, (bike_id,))
    updated_row = cursor.fetchone()
    conn.close()

    d = dict(updated_row)
    is_fav = bool(d.pop("is_fav", 0))
    res = row_to_bike_dict(sqlite3_row_mock(d))
    res["isFavorite"] = is_fav
    return res

@app.delete("/api/bikes/{bike_id}", tags=["Bikes"])
def delete_bike(bike_id: str):
    """Remove a motorcycle from the catalog."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bikes WHERE id = ?", (bike_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    cursor.execute("DELETE FROM bikes WHERE id = ?", (bike_id,))
    cursor.execute("DELETE FROM favorites WHERE bike_id = ?", (bike_id,))
    conn.commit()
    conn.close()
    return {"message": f"Bike '{bike_id}' successfully deleted."}

# --- COMPARISON ENGINE ENDPOINT ---

@app.get("/api/compare", response_model=CompareResponse, tags=["Comparison"])
def compare_bikes(
    id1: str = Query(..., description="First bike ID"),
    id2: str = Query(..., description="Second bike ID")
):
    """Perform server-side head-to-head comparison calculation between two bikes."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM bikes WHERE id = ?", (id1,))
    r1 = cursor.fetchone()
    cursor.execute("SELECT * FROM bikes WHERE id = ?", (id2,))
    r2 = cursor.fetchone()
    conn.close()

    if not r1 or not r2:
        raise HTTPException(status_code=404, detail="One or both bikes could not be found for comparison.")

    b1 = row_to_bike_dict(r1)
    b2 = row_to_bike_dict(r2)

    def calc_winner(val1, val2, higher_is_better=True, lower_is_better=False):
        win_class = "text-green-600 dark:text-green-400 font-bold better-spec"
        if val1 == val2:
            return 0, "", ""
        b1_wins = (val1 > val2) if higher_is_better else (val1 < val2)
        if b1_wins:
            return 1, win_class, "text-gray-500"
        else:
            return 2, "text-gray-500", win_class

    specs_config = [
        ("Price", "price", False, True, "₹"),
        ("Rating", "rating", True, False, "★"),
        ("Engine Capacity", "engine", True, False, "cc"),
        ("Max Power", "power", True, False, "bhp"),
        ("Peak Torque", "torque", True, False, "Nm"),
        ("Top Speed", "topSpeed", True, False, "km/h"),
        ("Mileage", "mileage", True, False, "kmpl"),
        ("Kerb Weight", "weight", False, True, "kg"),
        ("Fuel Tank", "fuelCapacity", True, False, "L"),
    ]

    b1_wins_count = 0
    b2_wins_count = 0
    specs_list = []

    for label, key, higher, lower, unit in specs_config:
        v1 = b1.get(key)
        v2 = b2.get(key)
        winner, b1_c, b2_c = calc_winner(v1, v2, higher, lower)
        if winner == 1:
            b1_wins_count += 1
        elif winner == 2:
            b2_wins_count += 1

        specs_list.append(SpecComparison(
            label=label,
            key=key,
            val1=v1,
            val2=v2,
            unit=unit,
            winner=winner,
            b1Class=b1_c,
            b2Class=b2_c
        ))

    overall_winner = None
    if b1_wins_count > b2_wins_count:
        overall_winner = b1["model"]
    elif b2_wins_count > b1_wins_count:
        overall_winner = b2["model"]
    else:
        overall_winner = "Tie"

    return CompareResponse(
        bike1=b1,
        bike2=b2,
        specs=specs_list,
        summary={
            "b1Wins": b1_wins_count,
            "b2Wins": b2_wins_count,
            "overallWinner": overall_winner,
            "totalSpecsCompared": len(specs_list)
        }
    )

# --- FILTER METADATA ENDPOINT ---

@app.get("/api/filters", response_model=FilterOptions, tags=["Filters"])
def get_filter_options():
    """Retrieve distinct brands, types, and min/max ranges for dynamic UI filter controls."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT brand FROM bikes ORDER BY brand ASC")
    brands = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT type FROM bikes ORDER BY type ASC")
    types = [r[0] for r in cursor.fetchall()]

    cursor.execute("SELECT MIN(price), MAX(price), MIN(engine), MAX(engine) FROM bikes")
    row = cursor.fetchone()
    conn.close()

    return FilterOptions(
        brands=brands,
        types=types,
        minPrice=row[0] or 100000.0,
        maxPrice=row[1] or 500000.0,
        minEngine=row[2] or 125.0,
        maxEngine=row[3] or 400.0
    )

# --- FAVORITES MANAGEMENT ENDPOINTS ---

@app.get("/api/favorites", response_model=List[str], tags=["Favorites"])
def get_favorites():
    """Return list of saved favorite bike IDs."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT bike_id FROM favorites ORDER BY created_at DESC")
    favs = [r[0] for r in cursor.fetchall()]
    conn.close()
    return favs

@app.post("/api/favorites/{bike_id}", tags=["Favorites"])
def add_favorite(bike_id: str):
    """Add a bike to saved favorites."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM bikes WHERE id = ?", (bike_id,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    cursor.execute("INSERT OR IGNORE INTO favorites (bike_id) VALUES (?)", (bike_id,))
    conn.commit()
    conn.close()
    return {"message": f"Bike '{bike_id}' added to favorites.", "bike_id": bike_id}

@app.delete("/api/favorites/{bike_id}", tags=["Favorites"])
def remove_favorite(bike_id: str):
    """Remove a bike from saved favorites."""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM favorites WHERE bike_id = ?", (bike_id,))
    conn.commit()
    conn.close()
    return {"message": f"Bike '{bike_id}' removed from favorites.", "bike_id": bike_id}

# --- STATIC FILES & ROOT FRONTEND SERVING ---

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
    return {"message": "MotoCompare Backend is running. Please access /docs for interactive Swagger API."}
