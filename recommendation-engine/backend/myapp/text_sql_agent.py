import os
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain import hub
from langchain.chains import create_sql_query_chain
from typing_extensions import TypedDict
from typing_extensions import Annotated

# load_dotenv()
# Global Variables
openai_api_key = os.getenv("OPENAI_API_KEY")
db = None
sql_chain = None
llm = None
query_prompt_template = hub.pull("langchain-ai/sql-query-system-prompt")

#Model classes
class State(TypedDict):
    question: str
    flight_query: str
    flight_result: str
    hotel_query: str
    hotel_result: str
    answer: str
class QueryOutput(TypedDict):
    """Generated SQL query."""
    query: Annotated[str, ..., "Syntactically valid SQL query."]

def createDB():
    """Assigns the database connection to the global variable `db`."""
    global db
    if db is None:  # Ensure it runs only once
        print("Initializing SQL Database connection...")
        database_url = os.environ.get('DATABASE_URL')
        db = SQLDatabase.from_uri(database_url)
    else:
        print("Database connection already initialized.")

def initialize_text_sql_agent():
    global sql_chain,llm
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=openai_api_key)
    createDB()  # Ensure DB is assigned
    sql_chain = create_sql_query_chain(llm, db)
    print("Text-SQL agent is ready.")

