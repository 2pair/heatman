from flask import Flask, render_template, g, request, jsonify
import sqlite3, csv, config, logging, time
from contextlib import closing
from datetime import datetime
from math import floor


app = Flask(__name__)
app.config.from_object(config)

# request info logging
log_file_handler = logging.FileHandler(app.config['LOG'])
log = app.logger
log.addHandler(log_file_handler)
log.setLevel(logging.INFO)


# ---------- database functions ----------
# upon recieveing a request connect to database
@app.before_request
def before_request():
    g.db = connect_db()


# always close the database after a request
@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()
        

# returns the name of the schema file
def get_schema():
    return app.config['SCHEMA']
    
    
# returns the name of the default table
def get_default_table():
    return app.config['TABLE_NAME']


# returns the name of the default database
def get_default_db():
    return app.config['DATABASE']

        
# open the database for doing activites
def connect_db(database=app.config['DATABASE']):
    return sqlite3.connect(database)


# create an empty database table based on schema
def init_db(schema=app.config['SCHEMA'], database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        with app.open_resource(schema, mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


# checks if a given table exists in the database
def table_exists(table, database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        db.text_factory = str
        cur = db.cursor()
        cur.execute(
            'SELECT name FROM sqlite_master' +
            ' WHERE type=\'table\'' +
            ' ORDER BY name')
        data = cur.fetchall()
        for entry in data:
            if table in entry:
                return True
        return False


# returns a list of the tables in the database
def get_tables(database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        db.text_factory = str
        cur = db.cursor()
        cur.execute(
            'SELECT name FROM sqlite_master' +
            ' WHERE type=\'table\'' +
            ' ORDER BY name')
        data = cur.fetchall()
        ret = []
        for tup in data:
            ret.append(tup[0])
        return ret
        
# returns a list of the Indices in the database
def get_indices(table=app.config['TABLE_NAME'], database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        db.text_factory = str
        cur = db.cursor()
        cur.execute(
            'SELECT * FROM sqlite_master' +
            ' WHERE type=\'index\' AND' +
            ' tbl_name=\'' + table + '\'')
        data = cur.fetchall()
        return data
        
        
# removes a table from the databsase
def delete_table(table, database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        cur = db.cursor()
        cur.execute('DROP table IF EXISTS ' + table)
        cur.commit()


# converts a csv file into a database table
def csv_to_table(
    csv_file=app.config['CSV'],
    table=app.config['TABLE_NAME'],
    database=app.config['DATABASE']):
    try:
        with open(csv_file,'rb') as c:
            r = csv.reader(c)
            for row in r:
                insert_row(tuple(row), table, database)
    except IOError as e:
        print 'CSV file not found. (' + e.errno + ': ' + e.strerror + ')'


# adds an entry to the database table from a passed in tuple
def insert_row(row, table=app.config['TABLE_NAME'], database=app.config['DATABASE']):
    with closing(connect_db(database)) as db:
        cur = db.cursor()
        cur.execute(
            'INSERT INTO ' + table + ' VALUES (?,?,?,?,?,?,?,?,?,?,?,?)', row)
        db.commit()


# creates an index within the database table
def create_table_index(
    column1, column2, 
    index=app.config['DB_INDEX'],
    table=app.config['TABLE_NAME'],
    database=app.config['DATABASE']):
    if column_exists(column1) and column_exists(column2):
        with closing(connect_db(database)) as db:
            cur = db.cursor()
            cur.execute(
                'CREATE INDEX ' + index + ' ON ' + table +
                ' (' + column1 + ', ' + column2 + ')')
            db.commit()
    

# fetches entries from the database inside the bounding box described by args,
# returns a tuple containing the latitude and longitude columns.
def get_data(nw_lat, nw_lng, se_lat, se_lng):
    start_time = time.time()
    
    # order the params like this because database is indexed from low to high
    params = (se_lat, nw_lat, nw_lng, se_lng)
    cur = g.db.cursor()
    cur.execute(
        'SELECT latitude, longitude FROM ' + app.config['TABLE_NAME'] +
        ' INDEXED BY ' + app.config['DB_INDEX'] +
        ' WHERE (latitude BETWEEN ? AND ?)' +
        ' AND (longitude BETWEEN ? AND ?)' +
        ' ORDER BY latitude, longitude ASC' ,params)
    data = cur.fetchall()

    elapsed_time = time.time() - start_time
    log.info(
        str(datetime.utcnow()) + ' : retrieved ' + str(len(data)) + 
        ' entries from db in ' + '{0:.5f}'.format(elapsed_time) + ' seconds')
    
    return data

# ---------- end database functions ----------


#validates a column name exists in the schema
# returns a boolean value
def column_exists(column):
    column = column.lower()
    with open(app.config['SCHEMA'], 'rb') as f:
        for line in f:
            if column in line.lower():
                return True
    return False


# gets the position of this column from the schema
# returns the position or None if it doesn't exist
def column_position(column):
    column = column.lower()
    with open(app.config['SCHEMA'], 'rb') as f:
        index = None
        for line in f:
            line = line.lower()
            if 'create table' in line:
                index = -1
            if index != None:
                index += 1
                if column in line:
                    return index
    return None
    

# creates a list of points aka, what the heatmap expects
def get_points(nw_lat, nw_lng, se_lat, se_lng, scale_factor):
    data = []
    # variables pertaining to positions in the tuple
    lat = 0
    lng = 1
    
    raw_data = get_data(nw_lat, nw_lng, se_lat, se_lng)
    start_time = time.time()
    
    # count the number of duplicate entries
    # add every 'scale_factor' duplicate to the list
    # add the first non-duplicate entry to the list
    # assumes duplicate entries are next to each other
    count = 0
    previous_entry = None
    for entry in raw_data:
        if entry == previous_entry:
            count += 1
            if count  >= scale_factor:
                count = 0
                data.append([entry[lat], entry[lng]])
        else:
            count = 0
            data.append([entry[lat], entry[lng]])
        previous_entry = entry
    
    elapsed_time = time.time() - start_time
    log.info(
        str(datetime.utcnow()) + ' : converted to list of ' + str(len(data)) + 
        ' objects in ' + '{0:.5f}'.format(elapsed_time) + ' seconds')
    
    return data 


# REST interface and page renderer
# takes latitude and longitude of two points to define our view bounding box
@app.route('/heatmap/', methods=['GET'])
def heatmap():
    # if we get no known queries, render the page 
    if (
        'nw_lat' not in request.args and
        'nw_lng' not in request.args and
        'se_lat' not in request.args and
        'se_lng' not in request.args and
        'sf'     not in request.args
    ):
        log.info(str(datetime.utcnow()) + ' : got page render request')
        return render_template('map.html')
    # else if we got some but not all known queries, its a bad request
    elif (
        'nw_lat' not in request.args or
        'nw_lng' not in request.args or
        'se_lat' not in request.args or
        'se_lng' not in request.args or
        'sf'     not in request.args
    ):
        log.info(str(datetime.utcnow()) + ' : got bad request')
        return bad_request('missing')
    
    nw_lat = request.args.get('nw_lat', type = float)
    nw_lng = request.args.get('nw_lng', type = float)
    se_lat = request.args.get('se_lat', type = float)
    se_lng = request.args.get('se_lng', type = float)
    scale_factor = request.args.get('sf'   , type = int)
    # make sure type conversion was successful
    if (
        nw_lat == None or
        nw_lng == None or
        se_lat == None or
        se_lng == None or
        scale_factor == None
    ):
        log.info(str(datetime.utcnow()) + ' : got bad request')
        return bad_request('malformed')
    
    # start handling our good request
    log.info(str(datetime.utcnow()) + ' : got good request')
    overall_start_time = time.time()
    
    # get all the points locations inside the box, then send them
    points = get_points(nw_lat, nw_lng, se_lat, se_lng, scale_factor)
    json_start_time = time.time()
    
    resp = jsonify(points=points)
    json_elapsed_time = time.time() - json_start_time
    
    log.info(
        str(datetime.utcnow()) + ' : converted to json in ' + 
        '{0:.5f}'.format(json_elapsed_time) + ' seconds')
    overall_elapsed_time = time.time() - overall_start_time
    log.info(
        str(datetime.utcnow()) + ' : request took ' + 
        '{0:.5f}'.format(overall_elapsed_time) + ' seconds')
      
    return resp
    
    
# message in case we are sent something that is non-compliant with the interface
def bad_request(verb='missing or malformed'):
    message = {
        'status': 400,
        'message': 'One or more fields was ' + verb + ' in the query string. ' +
            'Required fields are nw_lat, nw_lng, se_lat, and se_lng and are numeric.'}
    resp = jsonify(message)
    resp.status_code = 400
    
    return resp
    
    
if __name__ == '__main__':
    app.run()
