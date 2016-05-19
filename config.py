from os import path

# Config information for site

# debug
DEBUG      = False
# security
SECRET_KEY = 'ZDdhZDFkMzQ3ODU0NjAxZDA0MGRjNzBh'
USERNAME   = 'admin'
PASSWORD   = 'Password123!'
# files
BASE_DIR   = path.abspath(path.dirname(__file__))
SCHEMA     = 'schema.sql'
DATABASE   = 'static/db/GeoIPs.db'
CSV        = 'static/db/GeoLiteCityv6.csv'
LOG        = 'log/heatmap.log'
# database interface
TABLE_NAME = 'GeoIPs'
DB_INDEX   = 'geoloc'

