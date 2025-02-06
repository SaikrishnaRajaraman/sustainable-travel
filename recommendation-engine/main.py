import requests
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain import hub
from typing_extensions import TypedDict
from typing_extensions import Annotated
from langchain_community.tools.sql_database.tool import QuerySQLDatabaseTool
load_dotenv()

# Access the Global variables
openai_api_key = os.getenv("OPENAI_API_KEY")
db = None
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")


class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

class State(TypedDict):
    question: str
    query: str
    result: str
    answer: str

def write_query(state: State):
    """Generate SQL query to fetch information."""
    prompt = query_prompt_template.invoke(
        {
            "dialect": db.dialect,
            "top_k": 10,
            "table_info": db.get_table_info(),
            "input": state["question"],
        }
    )
    structured_llm = llm.with_structured_output(QueryOutput)
    result = structured_llm.invoke(prompt)
    return {"query": result["query"]}


def createDB():
    global db
    print("Assign DB to db")
    db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:pass@localhost:5432/sustainabletravel")
    # print(db.dialect)
    # print(db.get_usable_table_names())

    # res = db.run("SELECT source_iata_code FROM flight_emissions LIMIT 10;")
    # return db

def createChain(db):
    chain = create_sql_query_chain(llm, db)
    response = chain.invoke({"question": "Give me the top 5 distinct routes of flight to RDU sorted by ascending order for carbon emission"})
    print(response)
    response2 = chain.invoke({"question": "Give me the top 5 hotels in Raleigh sorted ascending by carbon emission"})
    print(response2)
    print(db.run(response))
    print(db.run(response2))

def execute_query(state: State):
    global db
    """Execute SQL query."""
    execute_query_tool = QuerySQLDatabaseTool(db=db)
    return {"result": execute_query_tool.invoke(state["query"])}

def generate_answer(state: State):
    """Answer question using retrieved information as context."""
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f'Question: {state["question"]}\n'
        f'SQL Query: {state["query"]}\n'
        f'SQL Result: {state["result"]}'
    )
    response = llm.invoke(prompt)
    return {"answer": response.content}

if __name__ == "__main__":
    createDB()
    # createChain(db)
    # query_prompt_template.messages[0].pretty_print()
    flight_query = write_query({"question": "Give me the top 5 distinct routes of flight to RDU sorted by ascending order for carbon emission"})
    result_flight_query = execute_query(flight_query)
    hotel_query = write_query({"question": "Give me the top 5 hotels in Raleigh sorted ascending by carbon emission"})
    result_hotel_query = execute_query(hotel_query)
    new_flight_state = {}
    for key in flight_query:
        new_flight_state[key] = flight_query[key]
    for key in result_flight_query:
        new_flight_state[key] = result_flight_query[key]
    new_hotel_state = {}
    for key in hotel_query:
        new_hotel_state[key] = hotel_query[key]
    for key in result_hotel_query:
        new_hotel_state[key] = result_hotel_query[key]
    state = State()
    state["question"] = "Generate me an itinerary for a sustainable trip to Raleigh. In one single itinerary, include me the hotel and flight options with combined carbon emissions sorted ina scending order"
    state["query"] = new_flight_state["query"] + "," + new_hotel_state["query"]
    state["result"] = new_flight_state["result"] + "," + new_hotel_state["result"]
    answer = generate_ans.wer(state)
    print(answer)
    

