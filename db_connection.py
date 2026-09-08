import os #allows you to interact with your OS 
from dotenv import load_dotenv 
from sqlalchemy import create_engine #imports the function that builds a connection to a database

load_dotenv()
#reads the env file and loads every 

def get_engine():
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT")
    db_name = os.getenv("DB_NAME")

    connection_string = (
        f"mlsql+mysqlconnector://{user}:{password}@{host}:{port}/{db_name}"
    )

    engine = create_engine(connection_string)
    #takes the connection string and builds an engine object 
    return engine

if __name__ == "__main__":
    engine = get_engine()
    try:
        with engine.connect as conn:
            print("Connected successfully")
    except Exception as e:
        print("Connection failed: ", e)