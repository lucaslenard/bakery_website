import pymysql


def connect_to_database():

    hostname = 'classmysql.engr.oregonstate.edu'
    username = 'cs340_lenardl'
    password = '9020'
    db = 'cs340_lenardl'

    connection = pymysql.connect(host=hostname, user=username, password=password, database=db)
    # connection = pymysql.connect('localhost', 'root', 'jamf1234', 'quiz3')
    return connection


def execute_query(connection=None, query=None):
    '''
    executes a given SQL query on the given db connection and returns a Cursor object

    db_connection: a MySQLdb connection object created by connect_to_database()
    query: string containing SQL query

    returns: A Cursor object as specified at https://www.python.org/dev/peps/pep-0249/#cursor-objects.
    You need to run .fetchall() or .fetchone() on that object to actually acccess the results.

    '''

    if connection is None:
        print("No connection to the database found! Have you called connect_to_database() first?")
        return None

    if query is None or len(query.strip()) == 0:
        print("query is empty! Please pass a SQL query in query")
        return None

    # Using tutorialspoint as a guide: https://www.tutorialspoint.com/python3/python_database_access.htm
    print(f"Executing %query: {query}")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # TODO: Sanitize the query before executing it
    cursor.execute(query)

    # Used when doing an insert - might need to split up if it causes issues with reads
    connection.commit()

    return cursor
