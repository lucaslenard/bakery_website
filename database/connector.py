import pymysql


def connect_to_database():

    hostname = 'classmysql.engr.oregonstate.edu'
    username = 'cs340_lenardl'
    password = '9020'
    db = 'cs340_lenardl'

    connection = pymysql.connect(host=hostname, user=username, password=password, database=db)
    return connection


def execute_query(query=None):

    connection = connect_to_database()

    # Using tutorialspoint as a guide: https://www.tutorialspoint.com/python3/python_database_access.htm
    print(f"Executing %query: {query}")
    cursor = connection.cursor(pymysql.cursors.DictCursor)

    # TODO: Sanitize the query before executing it
    cursor.execute(query)

    # Used when doing an insert - might need to split up if it causes issues with reads
    connection.commit()

    cursor.close()
    connection.close()

    return cursor
