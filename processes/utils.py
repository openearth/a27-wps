import configparser
from pathlib import Path
from sqlalchemy import select, func
from sqlalchemy import create_engine
service_path = Path(__file__).resolve().parents[1]
import logging
logger = logging.getLogger("PYWPS")


def read_config(file_name="configuration.txt"):
    """Reads the configuration file
    Returns:
        configuration object
    """
    cf_file = service_path / file_name
    cf = configparser.RawConfigParser()
    cf.read(cf_file)
    logger.info("TESTING CONFIGURATION") 
    
    return cf

def create_connection_db():
    """Creates a connection to the database
    Returns:
        connection object
    """
    cf = read_config()
    user = cf.get("PostGIS", "USER")
    password = cf.get("PostGIS", "PASSWORD")
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
        query = select(func.gws.get_locations_geojson())
        result = connection.execute(query).fetchone()[0]
    return result