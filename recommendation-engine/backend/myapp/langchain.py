import requests
import httpx
import asyncio
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from .text_sql_agent import State, QueryOutput, llm, db, query_prompt_template
from .models import Airport
from .calculate_miles import calculate_distance, DistanceUnit
from .utils import get_gcd_correction,calculate_carbon_emission,kg_to_metric_ton
import json
from asgiref.sync import sync_to_async

def get_enhanced_table_info_hotel(dest:str):
    base_info = db.get_table_info()
    routing_logic = """
    Special Query Instructions:
     1. For hotel queries:
       - Sort by carbon_emission in ascending order unless specified otherwise
       - Use appropriate LIMIT clause as specified in the question
       - Include hotel name and carbon emission in results
       - Convert {dest} to the corresponding city in which the airport is located.
            - For example:
            - RDU = 'Raleigh, NC'
            - LAX = 'Los Angeles, CA'
            - JFK = 'New York, NY'
    """
    return base_info + "\n" + routing_logic

def get_hotel_various_locations():
    base_info = db.get_table_info()
    routing_logic = """
    Special Query Instructions:
     1. For hotel queries:
       - Sort by carbon_emission in ascending order unless specified otherwise
       - Use appropriate LIMIT clause as specified in the question
       - Include hotel name and carbon emission in results
       - Query for records Where location = 'Various Locations'
    """
    return base_info + "\n" + routing_logic

def get_enhanced_table_info_flight():
    base_info = db.get_table_info()
    routing_logic = """
    Special Query Instructions:
    
    1. For flight routes queries:
       - Always include DISTINCT to avoid duplicate routes
       - Sort by carbon_emission in ascending order unless specified otherwise
       - Use appropriate LIMIT clause as specified in the question
       - Include all requested columns in the SELECT clause
    
       
    2. When searching for routes between airports:
       a) Direct routes query template:
          SELECT DISTINCT source_iata_code, destination_iata_code, 
                 flight_company as airline, carbon_emission
          FROM flight_emissions
          WHERE source_iata_code = '{source}' 
          AND destination_iata_code = '{dest}'
          ORDER BY carbon_emission ASC
          LIMIT {limit};
          
       b) Indirect routes query template:
          SELECT DISTINCT
              fe1.source_iata_code,
              fe1.destination_iata_code as layover,
              fe2.destination_iata_code as final_dest,
              fe1.flight_company as first_airline,
              fe2.flight_company as second_airline,
              (fe1.carbon_emission + fe2.carbon_emission) as total_carbon_emission
          FROM flight_emissions fe1
          JOIN flight_emissions fe2 
              ON fe1.destination_iata_code = fe2.source_iata_code
          WHERE fe1.source_iata_code = '{source}'
          AND fe2.destination_iata_code = '{dest}'
          AND fe2.destination_iata_code != fe1.source_iata_code
          ORDER BY total_carbon_emission ASC
          LIMIT {limit};
    """
    return base_info + "\n" + routing_logic

def suggest_alternative_routes(source: str, dest: str, llm) -> list:
    """Use LLM to suggest possible flight routes when none found in database."""
    suggestion_prompt = f"""
    As a flight route expert, suggest 3 possible flight routes from {source} to {dest}.
    Consider:
    1. Major hub airports between these locations
    2. Common airline routes
    3. Geographical proximity
    4. Typical connection points
    
    For each route:
    - Suggest possible airlines that commonly operate these routes
    - Exclude layover points as much as possible
    - Provide a confidence level for each suggestion
    - Provide great circular distance in miles between source and destination
    - Provide source link from where you extracted route information
    
    
    Format suggestions as valid JSON following this structure:
        "suggested_routes": [
            {{
                "type": "direct/indirect",
                "source": "{source}",
                "destination": "{dest}",
                "layover": "airport_code", // if indirect
                "likely_airlines": ["airline1", "airline2"],
                "confidence": "high/medium/low",
                "miles":"grea_cirular_distance(miles)"
                "source_of_route":"link_to_flight_route"
            }}
        ]
    """
    
    try:
        response = llm.invoke(suggestion_prompt)
        json_response = json.loads(response.content)
        return json_response.get("suggested_routes", [])
    except Exception as e:
        print(f"Error suggesting routes: {str(e)}")
        return []

def create_sql_query(state: State, question: str, mode: str, source:str, dest: str):
    """Generate SQL query to fetch information."""
    try:
        if mode == "flight":
            # First, try direct routes
            direct_question = (
                f"Generate a SQL query that will find direct flights. "
                f"{question}\n"
                f"Important: Ensure the query includes DISTINCT, sorts by carbon_emission ASC, "
                f"and uses the specified LIMIT."
            )
            prompt = query_prompt_template.invoke({
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": get_enhanced_table_info_flight(),
                "input": direct_question
            })
            
            structured_llm = llm.with_structured_output(QueryOutput,method="function_calling")
            result = structured_llm.invoke(prompt)
            state["flight_query"] = result["query"]
            
            # Execute direct flight query
            execute_query_tool = QuerySQLDatabaseTool(db=db)
            direct_results = execute_query_tool.invoke(state["flight_query"])
            # If no direct flights found, try indirect routes
            if not direct_results or 'No results' in direct_results or direct_results.isspace():
                indirect_question = (
                    f"Generate a SQL query that will find indirect flights with one layover. "
                    f"{question}\n"
                    f"Important: Use the indirect routes template with JOIN operation. Make sure the new route's combined distance is comparable(within 500 miles) to direct flights."
                )
                
                prompt = query_prompt_template.invoke({
                    "dialect": db.dialect,
                    "top_k": 10,
                    "table_info": get_enhanced_table_info_flight(),
                    "input": indirect_question
                })
                result = structured_llm.invoke(prompt)
                state["flight_query"] = result["query"]
            state["route_type"] = "direct" if direct_results and 'No results' not in direct_results and not direct_results.isspace() else "indirect"
            print("Final Flight Query",state["flight_query"])
        else:
            # Hotel query remains unchanged
            formatted_question = (
                f"Generate a SQL query that will {question}\n"
                f"Important: Sort by carbon_emission ASC and use the specified LIMIT."
            )
            prompt = query_prompt_template.invoke({
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": get_enhanced_table_info_hotel(dest),
                "input": formatted_question
            })
            
            structured_llm = llm.with_structured_output(QueryOutput,method="function_calling")
            result = structured_llm.invoke(prompt)
            state["hotel_query"] = result["query"]
            execute_query_tool = QuerySQLDatabaseTool(db=db)
            direct_results_hotel = execute_query_tool.invoke(state["hotel_query"])
            if not direct_results_hotel or 'No results' in direct_results_hotel or direct_results_hotel.isspace():
                various_locations_question =  """Find the top 5 hotels in 'Various Locations' with their carbon emissions.
                Sort by carbon_emission in ascending order."""
                prompt = query_prompt_template.invoke({
                    "dialect": db.dialect,
                    "top_k": 10,
                    "table_info": db.get_table_info(),
                    "input": various_locations_question
                })
                result = structured_llm.invoke(prompt)
                state["hotel_query"] = result["query"]
            print("Final Hotel Query",state["hotel_query"])
            
    except Exception as e:
        print(f"Error in create_sql_query: {str(e)}")
        raise

def process_query(source: str, dest: str) -> dict:
    """Process flight and hotel queries and generate an itinerary."""
    try:
        state: State = {}
        
        # Format flight query question with explicit requirements
        flight_question = (
            f"Find the top 5 routes from {source} to {dest}. "
            f"Include these columns: source_iata_code, destination_iata_code, "
            f"airline (as flight_company), and carbon_emission. "
            f"Sort by carbon_emission in ascending order."
        )
        
        # Format hotel query question
        hotel_question = (
            f"Find the top 5 hotels in {dest} with their carbon emissions. "
            f"Sort by carbon_emission in ascending order."
        )
        
        # Generate SQL queries
        create_sql_query(state, flight_question, "flight", source, dest)
        create_sql_query(state, hotel_question, "hotel", source, dest)
        
        # Execute queries
        execute_query(state, "flight",source,dest)
        execute_query(state, "hotel",source,dest)
        
        # Format the final question for generating the answer
        final_question = (
            f"Generate a sustainable travel itinerary for a trip from {source} to {dest} "
            f"formatted as a JSON object with two arrays: 'flights' and 'hotels'. "
            f"Each flight should include appropriate fields based on whether it's a {state.get('route_type', 'direct')} route. "
            f"Each hotel should include: name, location, and carbon_emission. "
            f"Both arrays should be sorted by carbon_emission in ascending order."
        )
        
        state["question"] = final_question
        return generate_answer(state)
        
    except Exception as e:
        print(f"Error in process_query: {str(e)}")
        return {"answer": f"An error occurred: {str(e)}"}

# def process_query(source: str, dest: str) -> dict:
#     """Synchronous wrapper for process_query_async."""
#     import asyncio
#     # Use asyncio.run for top-level async execution
#     return asyncio.run(process_query_async(source, dest))

def execute_query(state: State, mode: str, source: str, dest: str):
    """Execute the SQL query and store results in state."""
    try:
        execute_query_tool = QuerySQLDatabaseTool(db=db)
        query = state[f"{mode}_query"]
        result = execute_query_tool.invoke(query)
        if mode == "flight" and not result or 'No results' in result or result.isspace():
            # If no results found, suggest alternative routes
            result = suggest_alternative_routes(source,dest,llm)
            print("Suggesting alternate routes")
        state[f"{mode}_result"] = result
        if mode == "hotel":
            print("Hotel result",state["hotel_result"])
        else:
            print("Flight result",state["flight_result"])
    except Exception as e:
        print(f"Error executing {mode} query: {str(e)}")
        raise

def generate_answer(state: State) -> dict:
    """Generate a JSON-formatted itinerary based on query results."""
    try:
        route_type = state.get('route_type', 'direct')
        prompt = (
            "Using the following query results, create a JSON-formatted travel itinerary:\n\n"
            f"Route Type: {route_type}\n"
            f"Flight Results: {state['flight_result']}\n"
            f"Hotel Results: {state['hotel_result']}\n\n"
            "Format the response as a JSON object with this structure:\n"
            "{\n"
            "  'flights': [\n"
            "    // For direct flights:\n"
            "    {\n"
            "      'source': 'source_code',\n"
            "      'destination': 'dest_code',\n"
            "      'airline': 'airline_name',\n"
            "      'carbon_emission': number',\n"
            "      'confidence': 'high',\n"
            "      'source_of_route': 'DB'\n"
            "    },\n"
            "    // For indirect flights:\n"
            "    {\n"
            "      'source': 'source_code',\n"
            "      'layover': 'layover_code',\n"
            "      'destination': 'dest_code',\n"
            "      'first_airline': 'airline1_name',\n"
            "      'second_airline': 'airline2_name',\n"
            "      'carbon_emission': number',\n"
            "      'confidence': 'high',\n"
            "      'source_of_route': 'DB'\n"
            "    }\n"
            "   // For suggested routes:\n"
            "   {\n"
            "    'type': 'direct/indirect',\n"
            "    'source': '{source}',\n"
            "    'destination': '{dest}',\n"
            "    'layover': 'airport_code',,\n"
            "    'airline': ['airline1', 'airline2'],\n"
            "    'confidence': 'high/medium/low',\n"
            "    'miles':'grea_cirular_distance(miles)',\n"
            "    'source_of_route':'link_to_flight_route',\n"
            "    'carbon_emission': '0.0',\n"
            "    }\n"
            "  ],\n"
            "  'hotels': [\n"
            "    {\n"
            "      'name': 'hotel_name',\n"
            "      'location': 'city',\n"
            "      'carbon_emission': number\n"
            "    }\n"
            "  ]\n"
            "}\n\n"
            f"Use the appropriate flight format based on the route_type being {route_type}. "
            "Ensure all numeric values are properly formatted as numbers, not strings. "
            "Sort both arrays by carbon_emission in ascending order."
        )
        
        response = llm.invoke(prompt)
        
        # Try to parse the response as JSON
        try:
            json_response = json.loads(response.content)
            return {"answer": json_response}
        except json.JSONDecodeError:
            # If parsing fails, try to extract JSON from the response
            import re
            json_pattern = r'\{[\s\S]*\}'
            json_match = re.search(json_pattern, response.content)
            if json_match:
                json_str = json_match.group()
                try:
                    json_response = json.loads(json_str)
                    return {"answer": json_response}
                except json.JSONDecodeError:
                    raise ValueError("Could not parse response as JSON")
            else:
                raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        print(f"Error generating answer: {str(e)}")
        error_response = {
            "error": str(e),
            "flights": [],
            "hotels": []
        }

        return {"answer": error_response}

def process_bulk_csv(routes):
    """
    Processes multiple source-destination queries from a CSV file.
    Queries airport coordinates from the database and calculates distances.
    """
    results = []
    total_miles = 0
    total_emissions = 0

    for route in routes:
        try:
            source_code = route["source"]
            destination_code = route["destination"]

            if not source_code or not destination_code:
                continue  # Skip invalid entries

            # Fetch latitude & longitude from the database
            source_airport = Airport.objects.filter(iata=source_code).first()
            destination_airport = Airport.objects.filter(iata=destination_code).first()

            if not source_airport or not destination_airport:
                results.append({
                    "source": source_code,
                    "destination": destination_code,
                    "error": "Airport coordinates not found"
                })
                continue

            # Convert latitude & longitude to float
            lat1, lon1 = float(source_airport.latitude), float(source_airport.longitude)
            lat2, lon2 = float(destination_airport.latitude), float(destination_airport.longitude)

            # Calculate miles using Vincenty's formula
            distance_result = calculate_distance(
                lat1=lat1,
                lon1=lon1,
                lat2=lat2,
                lon2=lon2,
                unit=DistanceUnit.MILES
            )

            miles = distance_result.distance
            miles = get_gcd_correction(miles)
            emissions = calculate_carbon_emission(miles)
            emissions = kg_to_metric_ton(emissions)
            total_emissions += emissions 
            total_miles += miles  # Add to total miles

            results.append({
                "source": source_code,
                "destination": destination_code,
                "miles": miles
            })

        except Exception as e:
            results.append({
                "source": route.get("source"),
                "destination": route.get("destination"),
                "error": str(e)
            })


    

    return {"status": "success", "total_miles": total_miles, "results": results,"total_emissions": total_emissions} 


def get_airport_iata_codes():
    """
    Retrieves a list of all non-empty airport IATA codes from the database.
    
    Returns:
        dict: A dictionary with status and list of valid IATA codes
    """
    try:
        # Fetch only the IATA codes, filtering out null/empty values
        airports = Airport.objects.exclude(iata__isnull=True).exclude(iata="").values_list('iata', flat=True)
        
        # Convert QuerySet to list
        iata_codes = list(airports)
        
        return {
            "status": "success", 
            "count": len(iata_codes), 
            "iata_codes": iata_codes
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}
