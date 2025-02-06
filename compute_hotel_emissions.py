import pandas as pd
from models.ground_travel_model import GroundTravelModel
from utils.utils import ground_carbon_emission
import os
from openai import OpenAI
import json
from models.hotel_emission_model import HotelEmissionModel
import math


def classify_hotels_using_LLM(hotels_list):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key = openai_api_key)
    
    content = f"""
    {hotels_list}
    Classify all these hotels into one of the following groups.
    Resort
    NonResort
    Full Service Resort
    Full Service NonResort
    Limited Service
    Economy Segment Resort
    Economy Segment NonResort
    Midscale Segment Resort
    Midscale Segment NonResort
    Upper Midscale Segment Resort
    Upper Midscale Segment NonResort
    Upscale Segment Resort
    Upscale Segment NonResort
    Upper Upscale Segment Resort
    Upper Upscale Segment NonResort
    Luxury Segment Resort
    Luxury Segment NonResort
    Urban Location
    Suburban Location
    Rural/Highway Location
    Small Metro/Town Location
    Airport Hotel
    All Suites Or Extended Stay Hotel
    Bed & Breakfast Or Inn
    Convention Or Conference Hotel
    All Other Hotel (AOH)
    All Inclusive Resort (AIR)
    Beach Resort
    Integrated Resort
    Ski Resort
    All Other Resort (AOR)
    1 Star Resort
    1 Star NonResort
    2 Stars Resort
    2 Stars NonResort
    3 Stars Resort
    3 Stars NonResort
    4 Stars Resort
    4 Stars NonResort
    5 Stars Resort
    5 Stars NonResort
    Please return the classification in this format:
    [
        {{
            "hotel_name": "Hotel Name",
            "location": "City, State Code",
            "hotel_type": "Classified Hotel Type"
        }}
    ]

    Give me only the json response.
    """


#[
#     {"hotel_name": "HAMPTON INNS", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HILTON HOTELS", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MEADOWBROOK INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "EMBASSY SUITES", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "WYNDHAM", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MOUNTAINAIRE INN/ AZAL", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "DOUBLE TREE NEW BERN", "location": "New Bern, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "BEST WESTERN PARADISE", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HILTON CONVENTION CTR", "location": "", "hotel_type": "Convention Or Conference Hotel"},
#     {"hotel_name": "BLOWING ROCK INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "OAKHURST INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "COMFORT INNS", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "BEST WESTERN HICKORY", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "EMBASSY SUITES BIRMINGHAM", "location": "Birmingham, AL", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOMEWOOD SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "THE NORMANDY HOTEL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "DOUBLETREE HOTELS", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON BALTIMORE", "location": "Baltimore, MD", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON CAPITAL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON GARDEN INN", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "ALOFT RALEIGH HOTEL", "location": "Raleigh, NC", "hotel_type": "Limited Service"},
#     {"hotel_name": "QUALITY INNS", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "HAMPTON INN, BELL ROAD 13", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "COLLEGIAN HOTEL AND SUITE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "BEST WESTERN SMOKY MOU", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HAMPTON INN AND SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HILTON INTERNATIONALS", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "BEST WESTERN PLUS SADD", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HAMPTON INNS & SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "ROYAL SONESTA SAN JUAN", "location": "San Juan, PR", "hotel_type": "Upscale Segment Resort"},
#     {"hotel_name": "HILTON GARDEN INN LODGING", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "FORT COLLINS HILTON", "location": "Fort Collins, CO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTEL QUEEN MARY", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "OMNI WILLIAM PENN", "location": "Pittsburgh, PA", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "BEST WESTERN HOTELS", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HAMPTON INN OF WILKESBORO", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "ALOFT", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "DOUBLE TREE ROSEVILLE", "location": "Roseville, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON HOTELS KNOX AIRPOR", "location": "", "hotel_type": "Airport Hotel"},
#     {"hotel_name": "HILTON SEATTLE FD", "location": "Seattle, WA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "TRU BY HILTON DENVER", "location": "Denver, CO", "hotel_type": "Limited Service"},
#     {"hotel_name": "HILTON GARDEN INN OF AUBU", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "RWLV HOTEL FRONT DESK", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "SNOWBIRD CLIFF LODGE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "WALDORF", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "DRURY CHARLOTTE NORTH", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HILTON HOTELS CHICAGO", "location": "Chicago, IL", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "WILLIAM BLACK LODGE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "DAYS INNS/DAYSTOP", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "EMBASSY SUITES ATLA BK", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "GREAT WOLF LDG CONCORD", "location": "", "hotel_type": "All Other Resort (AOR)"},
#     {"hotel_name": "HELDRICH HOTEL", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HATTERAS ISLAND INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "FOUR POINTS HOTEL", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HTS - CONCORD - 2471", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "THE BEAUFORT HOTEL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "SFOZC - LDG - HP SAN CARL", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "NEWPORT CITY INN AND S", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "OMNI LA COSTA RESORT", "location": "Carlsbad, CA", "hotel_type": "Full Service Resort"},
#     {"hotel_name": "THE CALIFORNIA", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "DRURY INN GREENSBORO", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "CHARLOTTE HILTON", "location": "Charlotte, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HAMPTON INN INTERNATIONAL", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "SONESTA DENVER 1106", "location": "Denver, CO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "EMBASSY SUITES AIRPORT SA", "location": "", "hotel_type": "Airport Hotel"},
#     {"hotel_name": "MICROTEL INNS AND SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "THE DURHAM HOTEL (LODG", "location": "Durham, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HAMPTON INN AND SUITES CO", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "THE LONGLEAF HOTEL AND", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HAMPTON INN NEW BERN", "location": "New Bern, NC", "hotel_type": "Limited Service"},
#     {"hotel_name": "HILTON ADVPURCH8002367113", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MILLENNIUM KNICKERBOCKER", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "RED ROOF INN 0256", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "MARLTON HOTEL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "THE HOTEL AT UNIVERSIT", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HOMES TO SUITES BY HILTON", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "ELEVATION INN AND SUITES", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HAMPTON INN TIMONIUM", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "GEORGIA TECH HOTEL AND CO", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "SHERATON", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "DRURY INNS", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "CURIO HOTELS", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "ALASKAS POINT OF VIEW", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HARRAHS HOTELS ADV DEP", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "ORCA ADVENTURE LODGE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "WDW DISNEY RES", "location": "", "hotel_type": "Resort"},
#     {"hotel_name": "PINEOLA8287334979", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HILTON GARDEN INN RTP", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HAMILTON HOTEL DC", "location": "Washington, DC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS & SU", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HYATT REGENCY PHOENIX", "location": "Phoenix, AZ", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "CROWNE PLAZA", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS HOTE", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS PLYM", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS - KE", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "VAL AVIATOR HOTEL", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "KANUGA CONFERENCE CENTER", "location": "", "hotel_type": "Convention Or Conference Hotel"},
#     {"hotel_name": "HOTEL LODG  ALOFTRALE1", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HOLIDAY IN EXPRESS", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "VAL ALLEGHANY INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "CAESARS PLACE ADV RSVN", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "EMBASSY SUITES WINSTON SA", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "SWELL MOTEL", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN & SUITES", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HYATT REGENCY BALTIMORE", "location": "Baltimore, MD", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "EDGECAMP.COM", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HOLIDAY INN EXP & SUITES", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN GREENVILLE", "location": "Greenville, SC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS MOUN", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOLIDAY INN CAPITOL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELBOOKING SERVFEE", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "CAROLINA PINE INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HOLIDAY INN OCEANFRONT @", "location": "", "hotel_type": "Full Service Resort"},
#     {"hotel_name": "DISNEY Resort-WDW", "location": "", "hotel_type": "Resort"},
#     {"hotel_name": "HOLIDAY INN RESORT WRIGH", "location": "", "hotel_type": "Full Service Resort"},
#     {"hotel_name": "HYATT REGENCY SEATTLE", "location": "Seattle, WA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "KASA LIVIN  KASA LIVIN", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "LUXOR FRONT DESK", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "Cabinn Metro", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "OCRACOKE HARBOR INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "THE TRANQUIL HOUSE INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HILTON HOTELS SANDESTI", "location": "", "hotel_type": "Full Service Resort"},
#     {"hotel_name": "HAMPTON INN MONROE", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HAMPTON INNS MORGANTON", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HOLIDAY INN EXPRESS KNOX", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HARRAH'S HOTEL LV RESERV", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "THE UMSTEAD HOTEL", "location": "Cary, NC", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "STATEVIEW MARRIOTT", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON CHARLOTTE UNIVERS", "location": "Charlotte, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "TOWNEPLACE SUITES RALE", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "EMBASSY SUITES RALEIGH C", "location": "Raleigh, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELCOM72890143917648", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "PINEHURST ADV DEPOSIT", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "DOUBLETREE BY HILTON ASH", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MARRIOTT BROOKLYN BRID", "location": "Brooklyn, NY", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HAMPTON INN CHARLT UNIV", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "Orbitz 72890814248882", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "Orbitz 72890822205295", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "COURTYARD BY MARRIOTT", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "SPRINGHILL SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "DELTA HOTELS KALAMAZOO", "location": "Kalamazoo, MI", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "FAIRFIELD INN&SUITES C", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "RENAISSANCE HOTELS NAS", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "TOWNEPLACE SUITES BY M", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "COURTYARD CHARLOTTE WA", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "SPRINGHILL SUITES EAST", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "EXPEDIA 72894920078054", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "21C MUSEUM DURHAM", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HOTELCOM72057512126300", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "EXPEDIA 72896611802450", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "EXPEDIA 72896366655050", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "AC MARRIOTT RALEIGH N", "location": "Raleigh, NC", "hotel_type": "Upper Midscale Segment NonResort"},
#     {"hotel_name": "DOUBLETREE BY HILTON", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MICROTEL INN & SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "DOUBLETREE BY HILTON RAL", "location": "Raleigh, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "TOWNEPLACE SUITES", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "EXPEDIA 72902045038679", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "RENAISSANCE ASHEVILLE", "location": "Asheville, NC", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "HILTON GARDEN INN RALEIG", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HOTELCOM72057797590194", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "SPRINGHILL SUITES CARM", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "MARRIOTT RICHMOND F&B", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELCOM72057978723138", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "SPRINGHILL SUITES CHAR", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "RENAISSANCE RALEIGH F&", "location": "Raleigh, NC", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "AC MARRIOTT NY TIME", "location": "New York, NY", "hotel_type": "Upper Midscale Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN FLORENCE", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTEL BALLAST", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "UCLA LCC FRONT DESK", "location": "Los Angeles, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOMEWOOD STES ANAHEIM CC", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HOLIDAY INN EXPRESS PEMB", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "CROWNE PLAZA KNOXVILLE", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MARRIOTT ANAHEIM", "location": "Anaheim, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MARRIOTT CRYSTAL CITY", "location": "Crystal City, VA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOLIDAY INN AND SUITES", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MHR LNG BECH DWNTWN FD", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "THE OREAD TAPESTRY COLLE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "HYATT CENTRIC WAIKIKI", "location": "Waikiki, HI", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "HWS ATL NW/KENNESAW", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "Orbitz 72890824435826", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "CQ CHICAGO WACKER", "location": "Chicago, IL", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "THE BENSON HOTEL", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "MARRIOTT NEW ORLEANS", "location": "New Orleans, LA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "SPRINGHILL SUITES BY M", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HYATT REGENCY CAMBRIDGE", "location": "Cambridge, MA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HYATT REGENCY LONG BEACH", "location": "Long Beach, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "CAESARS HOTEL & CASINO", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN EXPRESS CONO", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HOMEWOOD SUITES GREENVIL", "location": "Greenville, SC", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "EXPEDIA 72892809143065", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HAMPTON INN & SUITES W", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HYATT AT OLIVE 8", "location": "Seattle, WA", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "HYATT REGENCY SAVANNAH", "location": "Savannah, GA", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "BERKELEY LAB GUEST HOUSE", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HILTON ANCHORAGE", "location": "Anchorage, AK", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "DOUBLETREE HOTEL", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "FAIRFIELD INN & SUITES", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "THE DUPONT HOTEL", "location": "Washington, DC", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "GRAND HYATT WASHINGTON", "location": "Washington, DC", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "HOTELCOM72894841439632", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "INTERCONTINENTAL ST PAU", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "HOLIDAY INN RALEIGH DOWN", "location": "Raleigh, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELCOM72057598031576", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HOTEL URSA", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HILTON TOWERS ARLING VA", "location": "Arlington, VA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HYATT REGENCY MINNEAPOLI", "location": "Minneapolis, MN", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HAMPTON INN NEWBERRY", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "HYATT PLACE GAINVILE DT", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "RAMADA RALEIGH", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "MARRIOTT SAVANNAH RIVE", "location": "Savannah, GA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MARRIOTT S DIEGO MARIN", "location": "San Diego, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELCOM72057716741964", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HOTELCOM72057738154562", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "SPRINGHILL SUITES CARY", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HOTEL HOTELBOOKING", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HYATT CENTRIC DOWNTOWN", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "MARRIOTT CONF CTR UNIV", "location": "", "hotel_type": "Convention Or Conference Hotel"},
#     {"hotel_name": "HYATT REGENCY DENVER CC", "location": "Denver, CO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "KIMPTON HOTEL MONACO SLC", "location": "Salt Lake City, UT", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "HOTELCOM72057798197991", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "EXPEDIA 72903511963095", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "HYATT REGENCY SAN ANTONI", "location": "San Antonio, TX", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "DOUBLETREE CHARLOTTE", "location": "Charlotte, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HILTON ST. LOUIS FRONTEN", "location": "St. Louis, MO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "SHERATON DENVER DWNTN", "location": "Denver, CO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HYATT REGENCY SAN FRAN A", "location": "San Francisco, CA", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "LUXOR - ADV DEP", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "HOTELCOM72057880848562", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "MARRIOTT GREENSBORO DT", "location": "Greensboro, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "EXPEDIA 72906810516657", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "MARRIOTT WESTFIELDS WA", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "DELTA PRINCE EDWARD", "location": "Prince Edward Island", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "HARRISONBURG DOUBLETREE", "location": "Harrisonburg, VA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HOTELSONE9042948065866", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "THE FAIRMONT HOTEL CHICA", "location": "", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "FSP LAKE JUNALUSKA ASSEMB", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "COURTYARD ASHEVILLE", "location": "Asheville, NC", "hotel_type": "Limited Service"},
#     {"hotel_name": "SPRINGHILL ASHEVILLE", "location": "Asheville, NC", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "BIG SKY RESORT LODGING", "location": "", "hotel_type": "Ski Resort"},
#     {"hotel_name": "RENAISSANCE RALEIGH", "location": "Raleigh, NC", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "MARRIOTT CRYSTAL GATEW", "location": "", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "MARRIOTT JW WASH DC", "location": "Washington, DC", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "FAIRFIELD INN&SUITES D", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "ATLANTA MARRIOTT CENTU", "location": "Atlanta, GA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "WACO RESIDENCE INN", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "HYATT PLACE RALEIGH NC", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "COURTYARD CHARLOTTE", "location": "Charlotte, NC", "hotel_type": "Limited Service"},
#     {"hotel_name": "RESIDENCE INN BLACKSBU", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "COURTYARD WINSTON-SALE", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "FAIRFIELD INN SAC AIR", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "HYATT PLACE CHARLOTTE AP", "location": "Charlotte, NC", "hotel_type": "Limited Service"},
#     {"hotel_name": "FAIRFIELD INN", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "WESTIN (WESTIN HOTELS)", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "RESIDENCE INN", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "FAIRFIELD INN & STES", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "AC MARRIOTT ATLANTA DT", "location": "Atlanta, GA", "hotel_type": "Upper Midscale Segment NonResort"},
#     {"hotel_name": "PHILA SHERATON UNIV CITY", "location": "Philadelphia, PA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "KANSAS CITY MARRIOTT", "location": "Kansas City, MO", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "COURTYARD BY MARRIOTT-", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "FAIRFIELD INN & SUITE", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "AC HOTELS BY MARRIOTT", "location": "", "hotel_type": "Upper Midscale Segment NonResort"},
#     {"hotel_name": "AC HOTEL GAINSVILLE DO", "location": "", "hotel_type": "Upper Midscale Segment NonResort"},
#     {"hotel_name": "FAIRFIELD INN EVANSVIL", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "TOWNEPLACE SUITES KILL", "location": "", "hotel_type": "All Suites Or Extended Stay Hotel"},
#     {"hotel_name": "RICHMOND MARRIOTT", "location": "Richmond, VA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "CHARLOTTE MARRIOTT CC", "location": "Charlotte, NC", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "COURTYARD BY MARRIOT", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "RENAISSANCE HOTELS SPR", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "THE LIMITED HOTEL", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "MARRIOTT CHICAGO M MIL", "location": "Chicago, IL", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "THE DINSMORE INN", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "WESTIN WASHINGTON DC CIT", "location": "Washington, DC", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "WESTIN O HARE FD", "location": "Chicago, IL", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "HYATT PLACE RALEIGH", "location": "", "hotel_type": "Limited Service"},
#     {"hotel_name": "SHERATON BOSTON FD", "location": "Boston, MA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "PU UNION CLUB HOTEL WL", "location": "", "hotel_type": "All Other Hotel (AOH)"},
#     {"hotel_name": "SHERATON LA JOLLA", "location": "La Jolla, CA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "PINEHURST LODGING", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "INN ON THE SQUARE", "location": "", "hotel_type": "Bed & Breakfast Or Inn"},
#     {"hotel_name": "W MINNEAPOLIS FOSHAY", "location": "Minneapolis, MN", "hotel_type": "Luxury Segment NonResort"},
#     {"hotel_name": "COMFORT INN & SUITES VT0", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "SHERATON GRD SEATTLE", "location": "Seattle, WA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "COMFORT INN & STES NC898", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "SHERATON INNER HARBOR", "location": "Baltimore, MD", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "CLARION INN ASHEVILLE AI", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "SHERATON NEW ORLEANS", "location": "New Orleans, LA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "COMFORT SUITES OH649", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "CAMBRIA-SAVANNAH GA989", "location": "", "hotel_type": "Upscale Segment NonResort"},
#     {"hotel_name": "SHERATON HOTELS INDY DWT", "location": "Indianapolis, IN", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "WESTIN SAVANNAH HRBR", "location": "Savannah, GA", "hotel_type": "Full Service NonResort"},
#     {"hotel_name": "FOUR POINTS BY SHERATO", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "ECONO LODGE NC153", "location": "", "hotel_type": "Economy Segment NonResort"},
#     {"hotel_name": "COMFORT INN", "location": "", "hotel_type": "Midscale Segment NonResort"},
#     {"hotel_name": "WESTIN HUNTSVILLE", "location": "Huntsville, AL", "hotel_type": "Upscale Segment NonResort"}
# ]
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Classify hotels into predefined categories based on provided list."},
                {"role": "user", "content": content}
            ],
            )
        output = response.choices[0].message.content
        print(output)
        output_lines = output.splitlines()
        output_lines = output_lines[1:-1]
        output = "\n".join(output_lines)
        print(output)
        flight_data = json.loads(output)
        return flight_data
    except Exception as e:
        print(f"An error occurred: {e}")

    return ""

def get_hotel_data():

    mean_emissions_path = 'mean_hotel_emissions.csv'

    hotel_data_path = 'hotel_data.xlsx'

    
    hotel_data = pd.read_excel("2022-24-ncsu-pcard.xlsx", sheet_name="2022-24-ncsu-HOTEL")
    unique_hotels = hotel_data['Vendor Name'].unique()
    print(unique_hotels)
    print("Number of unique hotels is : ",len(unique_hotels))

    hotel_emissions_data = []

    hotel_emission_averages = {}

    mean_emissions_data = pd.read_csv(mean_emissions_path)
    column_averages = mean_emissions_data.iloc[:, 4:].mean()
    hotel_averages = column_averages.to_dict()

    valid_values = [value for value in hotel_averages.values() if not math.isnan(value)]
    average_value = sum(valid_values) / len(valid_values)

    hotel_averages = {key: (value if not math.isnan(value) else average_value) for key, value in hotel_averages.items()}

    batch_size = 200

    for i in range(0,len(unique_hotels),batch_size):
        subset = unique_hotels[i:i + batch_size]
        classification_data = classify_hotels_using_LLM(subset)

        for item in classification_data:
            hotel_name = item["hotel_name"]
            location = item["location"]
            hotel_type = item["hotel_type"]

        if not location:
            emission = hotel_averages[hotel_type]
        else:
            hotel_row = mean_emissions_data[mean_emissions_data['Geography'] == location]
            if not hotel_row.empty:
                emission = hotel_row[hotel_type].values
            else:
                emission = hotel_averages[hotel_type]

            hotel_emission_model = HotelEmissionModel()   
            hotel_emission_model.hotel_name = hotel_name
            hotel_emission_model.hotel_type = hotel_type
            hotel_emission_model.location = location
            hotel_emission_model.carbon_emission = emission
            hotel_emissions_data.append(hotel_emission_model)


    return hotel_emissions_data         



                



    # for index, row in hotel_data.iterrows():