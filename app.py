import os
import requests
from datetime import datetime, date
from dotenv import load_dotenv
import streamlit as st
import math
import json

load_dotenv()

# API Keys loaded from .env only - never displayed
MAPS_API_KEY = os.getenv("MAPS_API_KEY", "")
FOURSQUARE_API_KEY = os.getenv("FOURSQUARE_API_KEY", "")
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

st.set_page_config(
    page_title="VoyageAI | Smart Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================================
# COMPREHENSIVE INDIAN CITIES DATABASE with COORDINATES and TOURIST SPOTS
# ============================================================================

CITIES_DB = {
    # North India
    "delhi": {"lat": 28.6139, "lon": 77.2090, "state": "Delhi", "type": "metro", "spots": ["Red Fort", "India Gate", "Qutub Minar", "Lotus Temple", "Humayun's Tomb", "Chandni Chowk", "Akshardham Temple"]},
    "manali": {"lat": 32.2396, "lon": 77.1887, "state": "Himachal Pradesh", "type": "hillstation", "spots": ["Solang Valley", "Hadimba Temple", "Rohtang Pass", "Old Manali", "Vashisht Hot Water Springs", "Jogini Falls", "Manali Sanctuary"]},
    "shimla": {"lat": 31.1048, "lon": 77.1734, "state": "Himachal Pradesh", "type": "hillstation", "spots": ["The Ridge", "Mall Road", "Jakhoo Temple", "Kufri", "Christ Church", "Summer Hill", "Green Valley"]},
    "dharamshala": {"lat": 32.2190, "lon": 76.3234, "state": "Himachal Pradesh", "type": "hillstation", "spots": ["McLeod Ganj", "Dalai Lama Temple", "Bhagsu Falls", "Triund Trek", "Kangra Fort", "War Memorial"]},
    "rishikesh": {"lat": 30.0869, "lon": 78.2676, "state": "Uttarakhand", "type": "spiritual", "spots": ["Lakshman Jhula", "Ram Jhula", "Triveni Ghat", "Neelkanth Mahadev Temple", "River Rafting", "Beatles Ashram", "Parmarth Niketan"]},
    "haridwar": {"lat": 29.9457, "lon": 78.1642, "state": "Uttarakhand", "type": "spiritual", "spots": ["Har Ki Pauri", "Mansa Devi Temple", "Chandi Devi Temple", "Ganga Aarti", "Daksha Mahadev Temple"]},
    "nainital": {"lat": 29.3803, "lon": 79.4637, "state": "Uttarakhand", "type": "hillstation", "spots": ["Naini Lake", "Naina Devi Temple", "Snow View Point", "Tiffin Top", "Mall Road", "Cave Garden", "Eco Cave Gardens"]},
    "mussoorie": {"lat": 30.4598, "lon": 78.0642, "state": "Uttarakhand", "type": "hillstation", "spots": ["Mall Road", "Gun Hill", "Kempty Falls", "Lal Tibba", "Company Garden", "Camel's Back Road"]},
    "jaipur": {"lat": 26.9124, "lon": 75.7873, "state": "Rajasthan", "type": "heritage", "spots": ["Hawa Mahal", "Amber Fort", "City Palace", "Jantar Mantar", "Nahargarh Fort", "Jaigarh Fort", "Albert Hall Museum", "Jal Mahal"]},
    "udaipur": {"lat": 24.5854, "lon": 73.7125, "state": "Rajasthan", "type": "heritage", "spots": ["Lake Pichola", "City Palace", "Jag Mandir", "Sahelion-ki-Bari", "Fateh Sagar Lake", "Vintage Car Museum", "Bagore-ki-Haveli"]},
    "jodhpur": {"lat": 26.2389, "lon": 73.0243, "state": "Rajasthan", "type": "heritage", "spots": ["Mehrangarh Fort", "Jaswant Thada", "Umaid Bhawan Palace", "Clock Tower", "Mandore Garden", "Rao Jodha Desert Park"]},
    "jaisalmer": {"lat": 26.9127, "lon": 70.9129, "state": "Rajasthan", "type": "desert", "spots": ["Jaisalmer Fort", "Sam Sand Dunes", "Patwon Ki Haveli", "Gadisar Lake", "Kuldhara Village", "Desert National Park"]},
    "pushkar": {"lat": 26.4905, "lon": 74.5522, "state": "Rajasthan", "type": "spiritual", "spots": ["Pushkar Lake", "Brahma Temple", "Savitri Temple", "Pushkar Camel Fair", "Varaha Temple", "Gurudwara Singh Sabha"]},
    "amritsar": {"lat": 31.6340, "lon": 74.8723, "state": "Punjab", "type": "spiritual", "spots": ["Golden Temple", "Jallianwala Bagh", "Wagah Border", "Durgiana Temple", "Gobindgarh Fort", "Partition Museum"]},
    
    # South India
    "chennai": {"lat": 13.0827, "lon": 80.2707, "state": "Tamil Nadu", "type": "metro", "spots": ["Marina Beach", "Kapaleeshwarar Temple", "Fort St. George", "Breezy Beach", "Government Museum", "Vandalur Zoo", "Elliot's Beach"]},
    "coimbatore": {"lat": 11.0168, "lon": 76.9558, "state": "Tamil Nadu", "type": "city", "spots": ["Marudamalai Temple", "Perur Patteeswarar Temple", "VOC Park", "Black Thunder Theme Park", "Isha Yoga Center", "Dhyanalinga Temple"]},
    "madurai": {"lat": 9.9252, "lon": 78.1198, "state": "Tamil Nadu", "type": "heritage", "spots": ["Meenakshi Amman Temple", "Thirumalai Nayakkar Palace", "Gandhi Museum", "Vaigai Dam", "Samarapalayam", "Koodal Azhagar Temple"]},
    "ooty": {"lat": 11.4102, "lon": 76.6950, "state": "Tamil Nadu", "type": "hillstation", "spots": ["Ooty Lake", "Doddabetta Peak", "Botanical Garden", "Rose Garden", "Avalanche Lake", "Wenlock Downs", "Pykara Lake"]},
    "kodaikanal": {"lat": 10.2381, "lon": 77.4891, "state": "Tamil Nadu", "type": "hillstation", "spots": ["Kodaikanal Lake", "Coaker's Walk", "Bryant Park", "Silver Cascade Falls", "Pillar Rocks", "Green Valley View", "Berijam Lake"]},
    "kanyakumari": {"lat": 8.0883, "lon": 77.5385, "state": "Tamil Nadu", "type": "coastal", "spots": ["Vivekananda Rock Memorial", "Thiruvalluvar Statue", "Kanyakumari Beach", "Sunrise/Sunset View", "Bhagavathy Amman Temple", "Gandhi Memorial"]},
    "bangalore": {"lat": 12.9716, "lon": 77.5946, "state": "Karnataka", "type": "metro", "spots": ["Lalbagh Garden", "Cubbon Park", "Bangalore Palace", "Tipu Sultan's Summer Palace", "Wonderla", "ISKCON Temple", "Bannerghatta Park"]},
    "mysore": {"lat": 12.2958, "lon": 76.6394, "state": "Karnataka", "type": "heritage", "spots": ["Mysore Palace", "Brindavan Gardens", "Chamundi Hill", "St. Philomena's Church", "Jaganmohan Palace", "Karanji Lake", "Mysore Zoo"]},
    "coorg": {"lat": 12.3375, "lon": 75.8069, "state": "Karnataka", "type": "hillstation", "spots": ["Abbey Falls", "Raja's Seat", "Talakaveri", "Dubare Elephant Camp", "Namdroling Monastery", "Iruppu Falls", "Mandalpatti"]},
    "gokarna": {"lat": 14.5458, "lon": 74.3161, "state": "Karnataka", "type": "coastal", "spots": ["Om Beach", "Kudle Beach", "Mahabaleshwar Temple", "Paradise Beach", "Half Moon Beach", "Yana Caves", "Mirjan Fort"]},
    "hampi": {"lat": 15.3350, "lon": 76.4600, "state": "Karnataka", "type": "heritage", "spots": ["Virupaksha Temple", "Vittala Temple", "Hampi Bazaar", "Elephant Stables", "Lotus Mahal", "Matanga Hill", "Queen's Bath"]},
    "hyderabad": {"lat": 17.3850, "lon": 78.4867, "state": "Telangana", "type": "metro", "spots": ["Charminar", "Golconda Fort", "Hussain Sagar", "Ramoji Film City", "Salar Jung Museum", "Birla Mandir", "Qutb Shahi Tombs"]},
    "vizag": {"lat": 17.6868, "lon": 83.2185, "state": "Andhra Pradesh", "type": "coastal", "spots": ["RK Beach", "Kailasagiri", "Submarine Museum", "Araku Valley", "Borra Caves", "Simhachalam Temple", "Yarada Beach"]},
    "kerala": {"lat": 10.8505, "lon": 76.2711, "state": "Kerala", "type": "backwaters", "spots": ["Munnar Tea Gardens", "Alleppey Backwaters", "Thekkady", "Wayanad", "Kovalam Beach", "Varkala Beach", "Athirappilly Falls", "Fort Kochi"]},
    "munnar": {"lat": 10.0891, "lon": 77.0593, "state": "Kerala", "type": "hillstation", "spots": ["Tea Museum", "Mattupetty Dam", "Echo Point", "Kundala Lake", "Anamudi Peak", "Lakkam Waterfalls", "Top Station"]},
    "alleppey": {"lat": 9.4981, "lon": 76.3388, "state": "Kerala", "type": "backwaters", "spots": ["Backwaters", "Houseboat Cruise", "Alappuzha Beach", "Pathiramanal Island", "Kuttanad", "Ambalappuzha Temple"]},
    "wayanad": {"lat": 11.6854, "lon": 76.1127, "state": "Kerala", "type": "hillstation", "spots": ["Edakkal Caves", "Chembra Peak", "Banasura Sagar Dam", "Soochipara Falls", "Kuruva Island", "Pookode Lake", "Muthanga Wildlife"]},
    "pondicherry": {"lat": 11.9141, "lon": 79.8145, "state": "Puducherry", "type": "coastal", "spots": ["Promenade Beach", "Auroville", "Sri Aurobindo Ashram", "French Quarter", "Paradise Beach", "Chunnambar Boat House", "Bharati Park"]},
    
    # West India
    "mumbai": {"lat": 19.0760, "lon": 72.8777, "state": "Maharashtra", "type": "metro", "spots": ["Gateway of India", "Marine Drive", "Juhu Beach", "Elephanta Caves", "Bandra-Worli Sealink", "Haji Ali Dargah", "Sanjay Gandhi Park", "Colaba Causeway"]},
    "pune": {"lat": 18.5204, "lon": 73.8567, "state": "Maharashtra", "type": "city", "spots": ["Shaniwar Wada", "Aga Khan Palace", "Sinhagad Fort", "Lonavala", "Khandala", "Raja Dinkar Kelkar Museum"]},
    "lonavala": {"lat": 18.7489, "lon": 73.4056, "state": "Maharashtra", "type": "hillstation", "spots": ["Tiger's Leap", "Lion's Point", "Bhushi Dam", "Karla Caves", "Rajmachi Fort", "Pawna Lake", "Imagica Theme Park"]},
    "mahabaleshwar": {"lat": 17.9309, "lon": 73.6638, "state": "Maharashtra", "type": "hillstation", "spots": ["Venna Lake", "Arthur's Seat", "Pratapgad Fort", "Lingmala Falls", "Kate's Point", "Elephant's Head Point", "Panchgani"]},
    "goa": {"lat": 15.2993, "lon": 74.1240, "state": "Goa", "type": "beach", "spots": ["Baga Beach", "Calangute Beach", "Fort Aguada", "Basilica of Bom Jesus", "Anjuna Beach", "Palolem Beach", "Dudhsagar Falls", "Chapora Fort"]},
    "ahmedabad": {"lat": 23.0225, "lon": 72.5714, "state": "Gujarat", "type": "metro", "spots": ["Sabarmati Ashram", "Kankaria Lake", "Adalaj Stepwell", "Science City", "Jama Masjid", "Sidi Saiyyed Mosque", "Modhera Sun Temple"]},
    "surat": {"lat": 21.1702, "lon": 72.8311, "state": "Gujarat", "type": "city", "spots": ["Dumas Beach", "Sarthana Nature Park", "Dutch Garden", "Suvali Beach", "Gopi Talav"]},
    "diu": {"lat": 20.7192, "lon": 70.9909, "state": "Diu", "type": "beach", "spots": ["Nagoa Beach", "Diu Fort", "Gangeshwar Temple", "Naida Caves", "Museum", "Jallandhar Beach", "Chakratirth Beach"]},
    
    # East India
    "kolkata": {"lat": 22.5726, "lon": 88.3639, "state": "West Bengal", "type": "metro", "spots": ["Howrah Bridge", "Victoria Memorial", "Dakshineswar Kali Temple", "Park Street", "Indian Museum", "Kalighat Temple", "Eden Gardens", "Science City"]},
    "darjeeling": {"lat": 27.0416, "lon": 88.2637, "state": "West Bengal", "type": "hillstation", "spots": ["Tiger Hill", "Darjeeling Himalayan Railway", "Batasia Loop", "Padmaja Naidu Park", "Mahakal Temple", "Tea Gardens", "Peace Pagoda"]},
    "gangtok": {"lat": 27.3358, "lon": 88.6154, "state": "Sikkim", "type": "hillstation", "spots": ["MG Marg", "Rumtek Monastery", "Tsomgo Lake", "Nathula Pass", "Banjhakri Falls", "Ganesh Tok", "Hanuman Tok"]},
    "bhubaneswar": {"lat": 20.2961, "lon": 85.8245, "state": "Odisha", "type": "heritage", "spots": ["Lingaraj Temple", "Udayagiri Khandagiri Caves", "Nandankanan Zoo", "Puri Beach", "Konark Sun Temple", "Dhauli Shanti Stupa"]},
    "puri": {"lat": 19.8135, "lon": 85.8312, "state": "Odisha", "type": "coastal", "spots": ["Jagannath Temple", "Puri Beach", "Konark Sun Temple", "Chilika Lake", "Gundicha Temple", "Sudarshan Craft Museum"]},
    "shillong": {"lat": 25.5788, "lon": 91.8933, "state": "Meghalaya", "type": "hillstation", "spots": ["Elephant Falls", "Laitlum Canyons", "Ward's Lake", "Shillong Peak", "Umiam Lake", "Don Bosco Museum", "Mary Help Church"]},
    
    # Central India
    "bhopal": {"lat": 23.2599, "lon": 77.4126, "state": "Madhya Pradesh", "type": "city", "spots": ["Upper Lake", "Sanchi Stupa", "Bhimbetka Caves", "Taj-ul-Masjid", "Van Vihar Park", "Birla Mandir"]},
    "indore": {"lat": 22.7196, "lon": 75.8577, "state": "Madhya Pradesh", "type": "city", "spots": ["Rajwada Palace", "Lal Bagh Palace", "Sarafa Bazaar", "Patalpani Falls", "Kanch Mandir", "Khajrana Ganesh Temple"]},
    "khajuraho": {"lat": 24.8318, "lon": 79.9199, "state": "Madhya Pradesh", "type": "heritage", "spots": ["Western Group of Temples", "Eastern Group Temples", "Khajuraho Dance Festival", "Raneh Falls", "Archaeological Museum"]}
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate accurate distance between coordinates"""
    R = 6371
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(min(1, math.sqrt(a)))
    return round(R * c, 1)

def get_city_coordinates(city_name):
    """Get coordinates from database"""
    city_name = city_name.lower().strip()
    if city_name in CITIES_DB:
        return CITIES_DB[city_name]
    for key, value in CITIES_DB.items():
        if key in city_name or city_name in key:
            return value
    return {"lat": 20.5937, "lon": 78.9629, "type": "unknown", "spots": ["Local Market", "Temple", "Park"]}

def get_distance_between_cities(origin, destination):
    """Get accurate distance between cities"""
    origin_data = get_city_coordinates(origin)
    dest_data = get_city_coordinates(destination)
    
    distance = haversine_distance(origin_data["lat"], origin_data["lon"], 
                                   dest_data["lat"], dest_data["lon"])
    
    # Road factor for Indian roads
    if distance < 100:
        road_factor = 1.1
    elif distance < 300:
        road_factor = 1.15
    elif distance < 800:
        road_factor = 1.2
    else:
        road_factor = 1.2
    
    road_distance = round(distance * road_factor, 1)
    
    if road_distance < 100:
        duration_mins = round((road_distance / 50) * 60)
    elif road_distance < 500:
        duration_mins = round((road_distance / 65) * 60)
    else:
        duration_mins = round((road_distance / 70) * 60)
    
    return {
        "straight_distance": distance,
        "road_distance": road_distance,
        "duration_mins": duration_mins,
        "duration_hours": round(duration_mins / 60, 1)
    }

def suggest_destinations(preference):
    """Suggest destinations based on preference"""
    suggestions = {
        "mountains": ["Manali", "Shimla", "Ooty", "Munnar", "Darjeeling", "Nainital"],
        "beach": ["Goa", "Gokarna", "Pondicherry", "Varkala", "Puri", "Diu"],
        "heritage": ["Jaipur", "Udaipur", "Jodhpur", "Madurai", "Mysore", "Hampi"],
        "spiritual": ["Rishikesh", "Haridwar", "Amritsar", "Pushkar", "Varanasi"],
        "backwaters": ["Alleppey", "Kumarakom", "Kollam", "Kochi"],
        "adventure": ["Rishikesh", "Manali", "Shillong", "Coorg", "Wayanad"],
        "wildlife": ["Jim Corbett", "Ranthambore", "Kaziranga", "Bandipur"],
        "cultural": ["Kolkata", "Mumbai", "Delhi", "Chennai", "Hyderabad"]
    }
    
    pref_key = preference.lower() if preference else "heritage"
    dest_list = suggestions.get(pref_key, suggestions["heritage"])
    
    result = []
    for dest in dest_list[:6]:
        dest_key = dest.lower()
        if dest_key in CITIES_DB:
            result.append({
                "name": dest,
                "state": CITIES_DB[dest_key]["state"],
                "type": CITIES_DB[dest_key]["type"],
                "spots": CITIES_DB[dest_key]["spots"][:3]
            })
        else:
            result.append({"name": dest, "state": "India", "type": "tourist", "spots": ["Popular attractions"]})
    return result

def calculate_travel_cost(distance_km, mode):
    if mode == "car":
        fuel_liters = distance_km / 15
        cost = round(fuel_liters * 102)
        return {"cost": cost, "breakdown": f"{round(fuel_liters, 1)}L petrol @ ₹102/L", "icon": "🚗"}
    elif mode == "train":
        if distance_km < 500:
            rate = 1.2
        elif distance_km < 1500:
            rate = 2.0
        else:
            rate = 3.0
        cost = round(distance_km * rate)
        return {"cost": cost, "breakdown": f"Sleeper class | ₹{rate}/km", "icon": "🚂"}
    elif mode == "flight":
        if distance_km < 500:
            cost = 3500
        elif distance_km < 1000:
            cost = 5500
        elif distance_km < 2000:
            cost = 8500
        else:
            cost = 12000
        return {"cost": cost, "breakdown": f"Economy class | {round(distance_km)} km", "icon": "✈️"}
    elif mode == "bike":
        fuel_liters = distance_km / 40
        cost = round(fuel_liters * 102)
        return {"cost": cost, "breakdown": f"{round(fuel_liters, 1)}L petrol", "icon": "🏍️"}
    else:
        return {"cost": 0, "breakdown": "Unknown", "icon": "❓"}

def get_hotel_estimate(destination, nights, budget_tier):
    dest_lower = destination.lower()
    premium_cities = ["mumbai", "delhi", "bangalore", "hyderabad", "chennai", "kolkata"]
    tourist_cities = ["goa", "manali", "jaipur", "udaipur", "ooty", "munnar", "darjeeling"]
    
    if any(city in dest_lower for city in premium_cities):
        rates = {"Budget": (2500, 4000), "Mid": (4500, 7000), "Premium": (8000, 20000)}
    elif any(city in dest_lower for city in tourist_cities):
        rates = {"Budget": (1500, 3000), "Mid": (3500, 6000), "Premium": (7000, 15000)}
    else:
        rates = {"Budget": (1000, 2000), "Mid": (2200, 4000), "Premium": (4500, 10000)}
    
    min_rate, max_rate = rates.get(budget_tier, rates["Mid"])
    avg_rate = (min_rate + max_rate) // 2
    total = avg_rate * nights
    
    return {
        "per_night_range": f"₹{min_rate:,} - ₹{max_rate:,}",
        "avg_per_night": avg_rate,
        "total": total
    }

def get_food_cost(nights, budget_tier):
    daily_food = {"Budget": (300, 500), "Mid": (600, 1000), "Premium": (1200, 2500)}
    min_food, max_food = daily_food.get(budget_tier, (500, 800))
    avg_daily = (min_food + max_food) // 2
    total = avg_daily * (nights + 1)
    return {"daily_range": f"₹{min_food} - ₹{max_food}", "total": total}

def get_rental_cost(vehicle_type, days):
    rates = {"Hatchback": (1200, 1800), "Sedan": (1800, 2800), "SUV": (2800, 4500), "Bike": (400, 700), "Scooter": (350, 600)}
    min_rate, max_rate = rates.get(vehicle_type, (1500, 2500))
    avg_rate = (min_rate + max_rate) // 2
    return {"per_day_range": f"₹{min_rate} - ₹{max_rate}", "total": avg_rate * days}

def get_spot_type(spot_name):
    spot_lower = spot_name.lower()
    if "fort" in spot_lower:
        return "🏰 Fort/Palace"
    elif "temple" in spot_lower or "church" in spot_lower or "mosque" in spot_lower:
        return "🛕 Temple/Church"
    elif "beach" in spot_lower:
        return "🏖️ Beach"
    elif "lake" in spot_lower or "falls" in spot_lower:
        return "💧 Lake/Waterfall"
    elif "park" in spot_lower or "garden" in spot_lower:
        return "🌳 Park/Garden"
    else:
        return "📍 Attraction"

# Professional styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }
    .stApp { background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%); }
    #MainMenu, footer, header { display: none; }
    .glass-card {
        background: rgba(18, 18, 30, 0.85);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 2rem;
        margin-bottom: 1.5rem;
    }
    .suggestion-card {
        background: rgba(99, 102, 241, 0.08);
        border: 1px solid rgba(99, 102, 241, 0.2);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.2s;
    }
    .suggestion-card:hover { background: rgba(99, 102, 241, 0.15); transform: translateY(-2px); }
    .hero {
        text-align: center;
        padding: 2.5rem;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1));
        border-radius: 32px;
        margin-bottom: 2rem;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    .hero h1 {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, #fff, #a5b4fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0;
    }
    .metric-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1rem;
        text-align: center;
    }
    .metric-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 1px; color: rgba(255, 255, 255, 0.5); }
    .metric-value { font-size: 1.8rem; font-weight: 700; color: white; }
    .stButton > button {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.6rem 1.5rem;
        font-weight: 500;
    }
    .stButton > button:hover { transform: translateY(-2px); opacity: 0.9; }
    .place-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 0.75rem 1rem;
        margin-bottom: 0.5rem;
    }
    .total-banner {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        border-radius: 20px;
        padding: 1.5rem;
        text-align: center;
        margin: 1.5rem 0;
    }
    .stTextInput > div > div > input, .stNumberInput > div > div > input {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        color: white;
    }
    hr { border-color: rgba(255, 255, 255, 0.1); }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'trip_data' not in st.session_state:
    st.session_state.trip_data = {}
if 'plan_generated' not in st.session_state:
    st.session_state.plan_generated = False
if 'show_suggestions' not in st.session_state:
    st.session_state.show_suggestions = False
if 'suggestions' not in st.session_state:
    st.session_state.suggestions = []

def next_step():
    st.session_state.step += 1
    st.rerun()

def prev_step():
    st.session_state.step -= 1
    st.rerun()

def reset_trip():
    for key in list(st.session_state.keys()):
        if key not in ['step', 'plan_generated']:
            del st.session_state[key]
    st.session_state.step = 1
    st.session_state.plan_generated = False
    st.rerun()

# Hero Section
st.markdown("""
<div class="hero">
    <h1>✈️ VoyageAI</h1>
    <p>Intelligent travel planning with real Indian destinations | Updated 2024</p>
</div>
""", unsafe_allow_html=True)

# STEP 1: ORIGIN
if st.session_state.step == 1 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📍 Where are you starting from?")
        
        st.markdown("**Popular starting points:**")
        major_cities = ["Chennai", "Mumbai", "Delhi", "Bangalore", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
        cols = st.columns(4)
        for i, city in enumerate(major_cities):
            with cols[i % 4]:
                if st.button(city, key=f"origin_{city}"):
                    st.session_state.trip_data['origin'] = city
                    next_step()
        
        st.markdown("---")
        origin = st.text_input("Or type your city", placeholder="e.g., Coimbatore, Nagpur, Lucknow")
        
        if st.button("Continue →", use_container_width=False):
            if origin and origin.strip():
                st.session_state.trip_data['origin'] = origin.strip()
                next_step()
            else:
                st.error("Please enter your starting city")
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 2: DESTINATION
elif st.session_state.step == 2 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🌍 Where do you want to go?")
        
        st.markdown("**What kind of vacation are you looking for?**")
        pref_cols = st.columns(4)
        preferences = [
            ("🏔️ Mountains", "mountains"), ("🏖️ Beaches", "beach"),
            ("🏰 Heritage", "heritage"), ("🕉️ Spiritual", "spiritual"),
            ("🚣 Backwaters", "backwaters"), ("🧗 Adventure", "adventure")
        ]
        
        for idx, (label, key) in enumerate(preferences):
            with pref_cols[idx % 4]:
                if st.button(label, key=f"pref_{key}"):
                    suggestions = suggest_destinations(key)
                    st.session_state.suggestions = suggestions
                    st.session_state.show_suggestions = True
        
        if st.session_state.show_suggestions and st.session_state.suggestions:
            st.markdown("---")
            st.markdown("**✨ Recommended destinations:**")
            sugg_cols = st.columns(3)
            for idx, dest in enumerate(st.session_state.suggestions[:6]):
                with sugg_cols[idx % 3]:
                    st.markdown(f"""
                    <div class="suggestion-card">
                        <strong>📍 {dest['name']}</strong>
                        <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5);">{dest['state']}</div>
                        <div style="font-size: 0.75rem; margin-top: 0.5rem;">{dest['spots'][0]}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Select {dest['name']}", key=f"sugg_{dest['name']}"):
                        st.session_state.trip_data['destination'] = dest['name']
                        next_step()
        
        st.markdown("---")
        st.markdown("**Popular destinations:**")
        popular_dests = ["Goa", "Manali", "Jaipur", "Ooty", "Mumbai", "Kerala", "Pondicherry", "Shimla"]
        dest_cols = st.columns(4)
        for i, dest in enumerate(popular_dests):
            with dest_cols[i % 4]:
                if st.button(dest, key=f"pop_{dest}"):
                    st.session_state.trip_data['destination'] = dest
                    next_step()
        
        st.markdown("---")
        other_dest = st.text_input("Or type your destination", placeholder="e.g., Hampi, Varanasi, Khajuraho")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                prev_step()
        with col2:
            if st.button("Continue →"):
                if other_dest and other_dest.strip():
                    st.session_state.trip_data['destination'] = other_dest.strip()
                    next_step()
                else:
                    st.warning("Please select or enter a destination")
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 3: TRAVEL MODE
elif st.session_state.step == 3 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🚗 How are you traveling?")
        
        origin = st.session_state.trip_data.get('origin', '')
        dest = st.session_state.trip_data.get('destination', '')
        
        if origin and dest:
            with st.spinner("Calculating distance..."):
                dist_data = get_distance_between_cities(origin, dest)
                st.session_state.trip_data['distance'] = dist_data['road_distance']
                st.session_state.trip_data['duration'] = dist_data['duration_mins']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">📏 Road Distance</div>
                        <div class="metric-value">{dist_data['road_distance']} km</div>
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">⏱️ Travel Time</div>
                        <div class="metric-value">{dist_data['duration_hours']} hrs</div>
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("**Select your mode:**")
        
        mode_cols = st.columns(4)
        modes = [("✈️ Flight", "flight"), ("🚂 Train", "train"), ("🚗 Car", "car"), ("🏍️ Bike", "bike")]
        
        for idx, (label, mode_key) in enumerate(modes):
            with mode_cols[idx]:
                if st.button(label, key=f"mode_{mode_key}", use_container_width=True):
                    st.session_state.trip_data['travel_mode'] = mode_key
                    next_step()
        
        if st.button("← Back"):
            prev_step()
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 4: STAY DURATION
elif st.session_state.step == 4 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🏨 How long will you stay?")
        
        nights = st.number_input("Number of nights", min_value=1, max_value=30, value=2, step=1)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                prev_step()
        with col2:
            if st.button("Continue →"):
                st.session_state.trip_data['nights'] = nights
                next_step()
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 5: BUDGET
elif st.session_state.step == 5 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 💰 Your budget preference")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🎒 Budget (₹800-2,000/night)", key="budget_budget", use_container_width=True):
                st.session_state.trip_data['budget_tier'] = "Budget"
                next_step()
        with col2:
            if st.button("🏨 Mid-Range (₹2,200-5,000/night)", key="budget_mid", use_container_width=True):
                st.session_state.trip_data['budget_tier'] = "Mid"
                next_step()
        with col3:
            if st.button("✨ Premium (₹5,000+/night)", key="budget_premium", use_container_width=True):
                st.session_state.trip_data['budget_tier'] = "Premium"
                next_step()
        
        if st.button("← Back"):
            prev_step()
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 6: FOOD PREFERENCE
elif st.session_state.step == 6 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🍽️ Food Preferences")
        
        cuisine_options = ["Local Specialties", "North Indian", "South Indian", "Asian", "Continental", "Seafood", "Street Food"]
        selected = st.selectbox("I prefer", cuisine_options, index=0)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                prev_step()
        with col2:
            if st.button("Continue →"):
                st.session_state.trip_data['cuisine'] = selected
                next_step()
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 7: RENTAL
elif st.session_state.step == 7 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🚙 Need local transport?")
        
        rental_needed = st.radio("Will you need a rental?", ["No", "Yes"], index=0)
        
        if rental_needed == "Yes":
            vehicle_type = st.selectbox("Vehicle type", ["Hatchback", "Sedan", "SUV", "Bike", "Scooter"])
            rental_days = st.number_input("Days needed", min_value=1, max_value=30, value=min(3, st.session_state.trip_data.get('nights', 3)))
            st.session_state.trip_data['rental'] = {'needed': True, 'type': vehicle_type, 'days': rental_days}
        else:
            st.session_state.trip_data['rental'] = {'needed': False}
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("← Back"):
                prev_step()
        with col2:
            if st.button("Continue →"):
                next_step()
        st.markdown('</div>', unsafe_allow_html=True)

# STEP 8: GENERATE PLAN
elif st.session_state.step == 8 and not st.session_state.plan_generated:
    with st.container():
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### ✅ Review & Generate")
        
        trip = st.session_state.trip_data
        dest_key = trip.get('destination', '').lower()
        dest_info = CITIES_DB.get(dest_key, {"state": "India", "spots": ["Local attractions"]})
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            **📍 From:** {trip.get('origin', 'N/A')}  
            **🌍 To:** {trip.get('destination', 'N/A')} ({dest_info.get('state', 'India')})  
            **🚗 Mode:** {trip.get('travel_mode', 'car').title()}  
            **🏨 Nights:** {trip.get('nights', 2)}  
            """)
        with col2:
            st.markdown(f"""
            **💰 Budget:** {trip.get('budget_tier', 'Mid')}  
            **🍽️ Cuisine:** {trip.get('cuisine', 'Local')}  
            **🚙 Rental:** {'Yes' if trip.get('rental', {}).get('needed') else 'No'}  
            **📏 Distance:** {trip.get('distance', 'Calculating')} km  
            """)
        
        if st.button("✨ Generate My Plan", use_container_width=True):
            with st.spinner("Creating your travel plan..."):
                dest = trip.get('destination', '')
                dest_lower = dest.lower()
                
                city_data = get_city_coordinates(dest)
                tourist_spots = city_data.get("spots", ["Local Market", "Temple", "Park"])[:6]
                
                travel_cost = calculate_travel_cost(trip.get('distance', 500), trip.get('travel_mode', 'car'))
                hotel_cost = get_hotel_estimate(dest, trip.get('nights', 2), trip.get('budget_tier', 'Mid'))
                food_cost = get_food_cost(trip.get('nights', 2), trip.get('budget_tier', 'Mid'))
                
                rental_cost = None
                if trip.get('rental', {}).get('needed'):
                    rental_cost = get_rental_cost(trip['rental']['type'], trip['rental']['days'])
                
                spots_with_icons = [{"name": spot, "type": get_spot_type(spot)} for spot in tourist_spots]
                
                restaurants = [
                    {"name": f"Popular {trip.get('cuisine', 'Local')} Restaurant", "cuisine": trip.get('cuisine', 'Local'), "price": "₹₹"},
                    {"name": "Local Food Court", "cuisine": "Multi-cuisine", "price": "₹₹"},
                    {"name": "Street Food Hub", "cuisine": "Street Food", "price": "₹"},
                    {"name": "Fine Dining", "cuisine": "International", "price": "₹₹₹"}
                ]
                
                total = travel_cost['cost'] + hotel_cost['total'] + food_cost['total']
                if rental_cost:
                    total += rental_cost['total']
                
                st.session_state.plan = {
                    'trip': trip,
                    'distance': trip.get('distance', 500),
                    'duration': trip.get('duration', 360),
                    'travel': travel_cost,
                    'hotel': hotel_cost,
                    'food': food_cost,
                    'rental': rental_cost,
                    'spots': spots_with_icons,
                    'restaurants': restaurants,
                    'total': total,
                    'city_info': city_data
                }
                st.session_state.plan_generated = True
                st.rerun()
        
        if st.button("← Back to edit"):
            prev_step()
        st.markdown('</div>', unsafe_allow_html=True)

# FINAL PLAN DISPLAY
elif st.session_state.plan_generated:
    plan = st.session_state.plan
    trip = plan['trip']
    
    st.balloons()
    
    st.markdown(f"""
    <div class="glass-card">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap;">
            <div>
                <div style="font-size: 0.7rem; color: #a5b4fc; text-transform: uppercase;">Your Custom Trip</div>
                <div style="font-size: 2rem; font-weight: 700; margin: 0.25rem 0;">
                    {trip.get('origin')} → {trip.get('destination')}
                </div>
                <div style="color: rgba(255,255,255,0.5);">{plan.get('city_info', {}).get('state', 'India')}</div>
            </div>
            <div>
                <div style="font-size: 0.7rem; color: rgba(255,255,255,0.5);">{plan['distance']} km road distance</div>
                <div style="font-size: 0.9rem;">{plan['travel']['icon']} {trip.get('travel_mode', 'car').title()}</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💰 Cost Breakdown")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">✈️ Travel</div>
            <div class="metric-value">₹{plan['travel']['cost']:,}</div>
            <div style="font-size: 0.7rem; opacity: 0.6;">{plan['travel']['breakdown']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🏨 Accommodation</div>
            <div class="metric-value">₹{plan['hotel']['total']:,}</div>
            <div style="font-size: 0.7rem; opacity: 0.6;">{plan['hotel']['per_night_range']} / night</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🍽️ Food</div>
            <div class="metric-value">₹{plan['food']['total']:,}</div>
            <div style="font-size: 0.7rem; opacity: 0.6;">{plan['food']['daily_range']} / day</div>
        </div>
        """, unsafe_allow_html=True)
    
    if plan['rental']:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">🚙 Local Transport</div>
            <div class="metric-value">₹{plan['rental']['total']:,}</div>
            <div style="font-size: 0.7rem; opacity: 0.6;">{plan['rental']['per_day_range']} / day</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="total-banner">
        <div style="font-size: 0.8rem; letter-spacing: 2px; text-transform: uppercase; opacity: 0.8;">Estimated Total</div>
        <div style="font-size: 3rem; font-weight: 700;">₹{plan['total']:,}</div>
        <div style="font-size: 0.8rem; opacity: 0.8;">Includes travel, stay, and meals</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏛️ Must-Visit Attractions")
    spots_cols = st.columns(2)
    for idx, spot in enumerate(plan['spots'][:6]):
        with spots_cols[idx % 2]:
            st.markdown(f"""
            <div class="place-card">
                <strong>{spot['type']} {spot['name']}</strong>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("### 🍴 Where to Eat")
    resto_cols = st.columns(2)
    for idx, resto in enumerate(plan['restaurants'][:4]):
        with resto_cols[idx % 2]:
            st.markdown(f"""
            <div class="place-card">
                <strong>{resto['name']}</strong>
                <div style="font-size: 0.75rem; opacity: 0.6;">{resto['cuisine']} · {resto['price']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with st.expander("💡 Travel Tips", expanded=False):
        st.markdown("""
        - **Book in advance:** Hotels and flights cheapest 30-45 days before
        - **Local transport:** Uber/Ola in cities, local autos for short distances
        - **Best season:** Oct-March ideal for most Indian destinations
        - **Packing:** Light cotton for plains, warm clothes for hill stations
        - **Safety:** Share itinerary, keep ID copies, stay hydrated
        """)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "📄 Download Plan",
            data=f"""VOYAGEAI TRAVEL PLAN
{'='*50}
From: {trip.get('origin')}
To: {trip.get('destination')}
Duration: {trip.get('nights')} nights
Mode: {trip.get('travel_mode', 'car').title()}
Distance: {plan['distance']} km

COSTS:
• Travel: ₹{plan['travel']['cost']:,}
• Hotel: ₹{plan['hotel']['total']:,}
• Food: ₹{plan['food']['total']:,}
{f'• Rental: ₹{plan["rental"]["total"]:,}' if plan['rental'] else ''}
{'='*50}
TOTAL: ₹{plan['total']:,}

ATTRACTIONS:
{chr(10).join(['• ' + s['name'] for s in plan['spots'][:6]])}

RESTAURANTS:
{chr(10).join(['• ' + r['name'] for r in plan['restaurants'][:4]])}
""",
            file_name=f"voyageai_{trip.get('destination', 'trip').lower().replace(' ', '_')}.txt",
            use_container_width=True
        )
    
    with col2:
        if st.button("🔄 Plan New Trip", use_container_width=True):
            reset_trip()