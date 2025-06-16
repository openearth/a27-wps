import configparser
from pathlib import Path
from sqlalchemy import create_engine
service_path = Path(__file__).resolve().parent


def read_config(file_name="configuration.txt") -> tuple:
    """Reads the configuration file
    Returns:
        cofngiruation object
    """
    cf_file = service_path / file_name
    cf = configparser.RawConfigParser()
    cf.read(cf_file)
    return cf

def create_connection_db():
    """Creates a connection to the database
    Returns:
        connection object
    """
    cf = read_config()
    user = cf.get("PostGIS", "USER")
    password = cf.get("POSTGIS", "PASSWORD")
    host = cf.get("PostGIS", "HOST")
    port = cf.get("PostGIS", "PORT")
    database = cf.get("PostGIS", "DATABASE")
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}")
    return engine

def get_locations():
    """Retrieves the locations from the database
    Returns:
        json of locations
    """
    engine = create_connection_db()
    with engine.connect() as connection:
        query = select()
    return locations