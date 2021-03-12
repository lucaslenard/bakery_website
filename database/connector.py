import logging
import pymysql

log = logging.getLogger(__name__)


def connect_to_database():

    # Hardcode Credentials in order to connect to database
    hostname = 'classmysql.engr.oregonstate.edu'
    username = ''
    password = ''
    db = ''

    try:
        connection = pymysql.connect(host=hostname, user=username, password=password, database=db)
        return connection

    except:
        log.error("Issue when trying to connect to database", exc_info=True)


def execute_query(query=None):

    connection = connect_to_database()

    # Using tutorialspoint as a guide: https://www.tutorialspoint.com/python3/python_database_access.htm
    print(f"Executing %query: {query}")
    log.info(f"Executing query: {query}")
    cursor = connection.cursor(pymysql.cursors.DictCursor)
    log.info(cursor)

    # TODO: Sanitize the query before executing it
    try:
        cursor.execute(query)
        connection.commit()

    except:
        connection.rollback()
        log.error(f"Issue when trying to run query: {query}", exc_info=True)

    cursor.close()
    connection.close()

    return cursor
