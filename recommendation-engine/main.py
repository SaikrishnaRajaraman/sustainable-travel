import requests
from langchain_community.utilities import SQLDatabase
from langchain.chains import create_sql_query_chain
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os
from langchain import hub
from typing_extensions import TypedDict
from typing_extensions import Annotated
load_dotenv()

# Access the Global variables
openai_api_key = os.getenv("OPENAI_API_KEY")
db = None


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

def queryRecords():
    print("Querying records from the database")
    db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:pass@localhost:5432/sustainabletravel")
    print(db.dialect)
    print(db.get_usable_table_names())
    # res = db.run("SELECT source_iata_code FROM flight_emissions LIMIT 10;")
    return db

def createChain(db):
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
    chain = create_sql_query_chain(llm, db)
    response = chain.invoke({"question": "Give me the top 5 distinct routes of flight to RDU sorted by ascending order for carbon emission"})
    print(response)
    response2 = chain.invoke({"question": "Give me the top 5 hotels in Raleigh sorted ascending by carbon emission"})
    print(response2)
    print(db.run(response))
    print(db.run(response2))

# def generate_answer():
#     """Answer question using retrieved information as context."""
#     prompt = (
#         "Given the following user question, corresponding SQL query, "
#         "and SQL result, answer the user question.\n\n"
#         f'Question: {state["question"]}\n'
#         f'SQL Query: {state["query"]}\n'
#         f'SQL Result: {state["result"]}'
#     )
#     response = llm.invoke(prompt)
#     return {"answer": response.content}

if __name__ == "__main__":
    db = queryRecords()
    # createChain(db)
    query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")
    query_prompt_template.messages[0].pretty_print()
