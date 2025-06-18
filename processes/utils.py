#  Copyright notice
#   --------------------------------------------------------------------
#   Copyright (C) 2025 Deltares for Project A27.
#   Main contributors: 
#   Ioanna Micha (ioanna.micha@deltares.nl)
#   Gerrit Hendriksen (Gerrit Hendriksen@deltares.nl)
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this library.  If not, see <http://www.gnu.org/licenses/>.
#   --------------------------------------------------------------------
#
# This tool is part of <a href="http://www.OpenEarth.eu">OpenEarthTools</a>.
# OpenEarthTools is an online collaboration to share and manage data and
# programming tools in an open source, version controlled environment.
# Sign up to recieve regular updates of this function, and to contribute
# your own tools.

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