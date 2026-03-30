import ollama
from app.database.init_db import init_db as create_db
from config import Config

#params => none
# this function checks if the required model is available in ollama, if not it will download it and make it ready to use
def init_ollam():
    req_llm=Config.LLM_NAME
    try:
        response = ollama.list()
        if req_llm in response['models']:
            print(f"Model {req_llm} is available.")
            print("Ready to use!")
            print(req_llm)
        else:
            print(f"Could not find model for {req_llm}")
            print("Downloading llama3.1:8b...")
            ollama.pull(req_llm)
            print("Download complete and ready to use!")
    except ConnectionError as e:
        raise ConnectionError from e
    except Exception as e:
        raise Exception from e

def init_db(Default_DB_name,new_DB_name,table_script,test_script):
    print("Initializing database...")
    create_db(Default_DB_name,new_DB_name,table_script,test_script)
    print("Database initialized!")

# create the new database and tables
try:
    init_db(Config.DEFAULT_DB_NAME,Config.DB_NAME,'app/database/init_db/create_tables.sql','app/database/init_db/test_data.sql')
    init_ollam()
except Exception as e:
    print(f"Connection error: {e}")
