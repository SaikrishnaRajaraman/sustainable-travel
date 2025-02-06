import requests
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
from .text_sql_agent import State, QueryOutput, llm, db, query_prompt_template

def create_sql_query(state, question,mode):
    """Generate SQL query to fetch information."""
    try:
        prompt = query_prompt_template.invoke(
            {
                "dialect": db.dialect,
                "top_k": 10,
                "table_info": db.get_table_info(),
                "input": question,
            }
        )
        structured_llm = llm.with_structured_output(QueryOutput)
        result = structured_llm.invoke(prompt)
        if mode == "flight":
            state["flight_query"] = result["query"]
        else:
            state["hotel_query"] = result["query"]
    except Exception as e:
        print(e)

#should run per request
def execute_query(state: State, mode):
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    if mode == "flight":
        state["flight_result"] = execute_query_tool.invoke(state["flight_query"])
    else:
        state["hotel_result"] = execute_query_tool.invoke(state["hotel_query"])

#should run per request
def generate_answer(state: State):
    prompt = (
        "Given the following user question, corresponding SQL queries for flight and hotel, "
        "and SQL results, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Flight Query: {state["flight_query"]}\n'
        f'SQL Hotel Query: {state["hotel_query"]}\n'
        f'SQL Flight Result: {state["flight_result"]}\n'
        f'SQL Hotel Result: {state["hotel_result"]}\n'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

def process_query(source,dest):
    print("inside process_query")
    state: State = {}
    question_flight = f"Give me the top 5 distinct routes of flight from {source} to {dest} sorted by ascending order with respect to carbon emission"
    question_hotel = f"Give me the top 5 hotels in {dest} sorted ascending by carbon emission"
    create_sql_query(state,question_flight,"flight")
    create_sql_query(state,question_hotel,"hotel")
    execute_query(state,"flight")
    execute_query(state,"hotel")
    state["question"] = "Generate me an itinerary for a sustainable trip to Raleigh. In one single itinerary, include me the hotel and flight options with combined carbon emissions sorted in a scending order"
    # # print(state["flight_query"],state["flight_result"])
    print("State:",state.keys())   
    answer = generate_answer(state)
    return answer

    
