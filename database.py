import sqlite3
import json
import os
from typing import List, Dict, Any

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "motocompare.db")

INITIAL_BIKES = [
    {
        "id": "ns400z",
        "brand": "Bajaj",
        "model": "Pulsar NS400Z",
        "price": 185000,
        "priceDisplay": "₹1.85 Lakh",
        "engine": 373.3,
        "mileage": 28.0,
        "power": 40.0,
        "torque": 35.0,
        "topSpeed": 165.0,
        "weight": 174.0,
        "fuelCapacity": 12.0,
        "brakes": "Dual Channel ABS, 320mm Front Disc",
        "suspension": "USD Fork / Monoshock",
        "type": "Naked",
        "rating": 4.5,
        "image": "https://images.unsplash.com/photo-1558981403-c5f9899a28bc?auto=format&fit=crop&q=80&w=800",
        "pros": ["Aggressive pricing", "Powerful 373cc engine", "Good handling & styling"],
        "cons": ["Slight vibrations at top end", "Instrument cluster feels basic"],
        "features": ["Ride-by-wire", "Switchable Traction Control", "4 Ride Modes", "LED Projector Headlamp"]
    },
    {
        "id": "mt15",
        "brand": "Yamaha",
        "model": "MT-15 V2",
        "price": 168000,
        "priceDisplay": "₹1.68 Lakh",
        "engine": 155.0,
        "mileage": 45.0,
        "power": 18.1,
        "torque": 14.1,
        "topSpeed": 130.0,
        "weight": 141.0,
        "fuelCapacity": 10.0,
        "brakes": "Dual Channel ABS",
        "suspension": "USD Fork / Linked Monoshock",
        "type": "Naked",
        "rating": 4.6,
        "image": "https://images.unsplash.com/photo-1590219598850-201633512fce?auto=format&fit=crop&q=80&w=800",
        "pros": ["Excellent mileage", "VVA technology for top-end pull", "Very lightweight and agile"],
        "cons": ["Stiff suspension setup", "Pillion seat is very small"],
        "features": ["VVA (Variable Valve Actuation)", "Assist & Slipper Clutch", "Traction Control System", "Aluminum Swingarm"]
    },
    {
        "id": "classic350",
        "brand": "Royal Enfield",
        "model": "Classic 350",
        "price": 193000,
        "priceDisplay": "₹1.93 Lakh",
        "engine": 349.0,
        "mileage": 35.0,
        "power": 20.2,
        "torque": 27.0,
        "topSpeed": 115.0,
        "weight": 195.0,
        "fuelCapacity": 13.0,
        "brakes": "Dual Channel ABS",
        "suspension": "Telescopic / Twin Tube",
        "type": "Cruiser",
        "rating": 4.7,
        "image": "https://images.unsplash.com/photo-1616422285623-aa42220d8d24?auto=format&fit=crop&q=80&w=800",
        "pros": ["Timeless design", "Refined J-series engine", "Excellent low-end torque"],
        "cons": ["Heavy weight", "Not meant for high speeds"],
        "features": ["Retro Styling", "Tripper Navigation (Optional)", "USB Charging Port", "Analog-Digital Instrument Cluster"]
    },
    {
        "id": "duke390",
        "brand": "KTM",
        "model": "Duke 390 (2024)",
        "price": 310000,
        "priceDisplay": "₹3.10 Lakh",
        "engine": 399.0,
        "mileage": 25.0,
        "power": 46.0,
        "torque": 39.0,
        "topSpeed": 170.0,
        "weight": 168.0,
        "fuelCapacity": 15.0,
        "brakes": "Supermoto ABS, 320mm Front",
        "suspension": "Adjustable USD / Adjustable Monoshock",
        "type": "Naked",
        "rating": 4.8,
        "image": "https://images.unsplash.com/photo-1568772585407-9361f9bf3a87?auto=format&fit=crop&q=80&w=800",
        "pros": ["Explosive performance", "Fully adjustable suspension", "Tech-loaded TFT display"],
        "cons": ["Expensive", "Aggressive power delivery not for beginners"],
        "features": ["Cornering ABS", "Quickshifter+", "Launch Control", "TFT Display with Bluetooth"]
    },
    {
        "id": "rtr310",
        "brand": "TVS",
        "model": "Apache RTR 310",
        "price": 242000,
        "priceDisplay": "₹2.42 Lakh",
        "engine": 312.12,
        "mileage": 30.0,
        "power": 35.6,
        "torque": 28.7,
        "topSpeed": 150.0,
        "weight": 169.0,
        "fuelCapacity": 11.0,
        "brakes": "Dual Channel ABS",
        "suspension": "KYB USD / Monoshock",
        "type": "Naked",
        "rating": 4.4,
        "image": "https://images.unsplash.com/photo-1591321040449-35a16d5cbce8?auto=format&fit=crop&q=80&w=800",
        "pros": ["Segment-first features", "Punchy mid-range", "Striking looks"],
        "cons": ["Vibrations at high RPMs", "Engine heat in traffic"],
        "features": ["Climate Control Seat", "Cruise Control", "Dynamic Headlight", "5 Ride Modes"]
    },
    {
        "id": "cb350",
        "brand": "Honda",
        "model": "CB350",
        "price": 199000,
        "priceDisplay": "₹1.99 Lakh",
        "engine": 348.36,
        "mileage": 35.0,
        "power": 21.07,
        "torque": 30.0,
        "topSpeed": 120.0,
        "weight": 187.0,
        "fuelCapacity": 15.2,
        "brakes": "Dual Channel ABS",
        "suspension": "Telescopic / Twin Hydraulic",
        "type": "Cruiser",
        "rating": 4.5,
        "image": "https://images.unsplash.com/photo-1599815074211-5a02da3c945b?auto=format&fit=crop&q=80&w=800",
        "pros": ["Extremely refined engine", "Light clutch pull", "Good build quality"],
        "cons": ["Tall gearing requires frequent shifting in city", "Conservative styling"],
        "features": ["Honda Smartphone Voice Control", "Selectable Torque Control (HSTC)", "Assist & Slipper Clutch", "LED Lighting"]
    }
]

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    # Bikes table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bikes (
            id TEXT PRIMARY KEY,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            price REAL NOT NULL,
            priceDisplay TEXT,
            engine REAL NOT NULL,
            mileage REAL NOT NULL,
            power REAL NOT NULL,
            torque REAL NOT NULL,
            topSpeed REAL NOT NULL,
            weight REAL NOT NULL,
            fuelCapacity REAL NOT NULL,
            brakes TEXT,
            suspension TEXT,
            type TEXT NOT NULL,
            rating REAL DEFAULT 4.0,
            image TEXT,
            pros_json TEXT,
            cons_json TEXT,
            features_json TEXT
        )
    """)

    # User favorites table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS favorites (
            bike_id TEXT PRIMARY KEY,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (bike_id) REFERENCES bikes(id) ON DELETE CASCADE
        )
    """)

    # Seed initial data if table is empty
    cursor.execute("SELECT COUNT(*) FROM bikes")
    count = cursor.fetchone()[0]
    if count == 0:
        for bike in INITIAL_BIKES:
            cursor.execute("""
                INSERT INTO bikes (
                    id, brand, model, price, priceDisplay, engine, mileage, power, torque,
                    topSpeed, weight, fuelCapacity, brakes, suspension, type, rating,
                    image, pros_json, cons_json, features_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                bike["id"],
                bike["brand"],
                bike["model"],
                bike["price"],
                bike.get("priceDisplay", f"₹{(bike['price'] / 100000):.2f} Lakh"),
                bike["engine"],
                bike["mileage"],
                bike["power"],
                bike["torque"],
                bike["topSpeed"],
                bike["weight"],
                bike["fuelCapacity"],
                bike.get("brakes", "Disc Brakes"),
                bike.get("suspension", "Telescopic / Monoshock"),
                bike["type"],
                bike.get("rating", 4.5),
                bike.get("image", ""),
                json.dumps(bike.get("pros", [])),
                json.dumps(bike.get("cons", [])),
                json.dumps(bike.get("features", []))
            ))
    conn.commit()
    conn.close()

def row_to_bike_dict(row: sqlite3.Row) -> Dict[str, Any]:
    if not row:
        return {}
    d = dict(row)
    d["pros"] = json.loads(d.pop("pros_json") or "[]")
    d["cons"] = json.loads(d.pop("cons_json") or "[]")
    d["features"] = json.loads(d.pop("features_json") or "[]")
    return d
