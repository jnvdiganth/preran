from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class BikeBase(BaseModel):
    id: str = Field(..., description="Unique identifier for the motorcycle (slug)")
    brand: str = Field(..., description="Manufacturer brand name (e.g. Bajaj, KTM, Yamaha)")
    model: str = Field(..., description="Motorcycle model name")
    price: float = Field(..., description="Ex-showroom price in INR")
    priceDisplay: Optional[str] = Field(None, description="Formatted price string e.g. ₹1.85 Lakh")
    engine: float = Field(..., description="Engine displacement in cc")
    mileage: float = Field(..., description="Fuel efficiency in kmpl")
    power: float = Field(..., description="Max power output in bhp")
    torque: float = Field(..., description="Peak torque in Nm")
    topSpeed: float = Field(..., description="Top speed in km/h")
    weight: float = Field(..., description="Kerb weight in kg")
    fuelCapacity: float = Field(..., description="Fuel tank capacity in Liters")
    brakes: Optional[str] = Field("Dual Channel ABS", description="Braking setup")
    suspension: Optional[str] = Field("USD / Monoshock", description="Suspension details")
    type: str = Field("Naked", description="Category e.g. Naked, Cruiser, Sport, Adventure")
    rating: Optional[float] = Field(4.5, description="User or expert rating out of 5")
    image: Optional[str] = Field("", description="Image URL")
    pros: List[str] = Field(default_factory=list, description="List of pros")
    cons: List[str] = Field(default_factory=list, description="List of cons")
    features: List[str] = Field(default_factory=list, description="Key features")

class BikeCreate(BikeBase):
    pass

class BikeUpdate(BaseModel):
    brand: Optional[str] = None
    model: Optional[str] = None
    price: Optional[float] = None
    priceDisplay: Optional[str] = None
    engine: Optional[float] = None
    mileage: Optional[float] = None
    power: Optional[float] = None
    torque: Optional[float] = None
    topSpeed: Optional[float] = None
    weight: Optional[float] = None
    fuelCapacity: Optional[float] = None
    brakes: Optional[str] = None
    suspension: Optional[str] = None
    type: Optional[str] = None
    rating: Optional[float] = None
    image: Optional[str] = None
    pros: Optional[List[str]] = None
    cons: Optional[List[str]] = None
    features: Optional[List[str]] = None

class BikeResponse(BikeBase):
    isFavorite: Optional[bool] = False

class SpecComparison(BaseModel):
    label: str
    key: str
    val1: Any
    val2: Any
    unit: str = ""
    winner: Optional[int] = None  # 1 if bike 1 wins, 2 if bike 2 wins, 0 if tie, None if not comparable
    b1Class: str = ""
    b2Class: str = ""

class CompareResponse(BaseModel):
    bike1: BikeBase
    bike2: BikeBase
    specs: List[SpecComparison]
    summary: Dict[str, Any]

class FilterOptions(BaseModel):
    brands: List[str]
    types: List[str]
    minPrice: float
    maxPrice: float
    minEngine: float
    maxEngine: float
