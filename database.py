import sqlite3

DB = "data.db"

def connect():
    return sqlite3.connect(DB, check_same_thread=False)


conn = connect()
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS calendar(

day TEXT PRIMARY KEY,
person TEXT,
color TEXT

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS requests(

id INTEGER PRIMARY KEY AUTOINCREMENT,
day TEXT,
sender TEXT,
receiver TEXT,
status TEXT

)
""")

conn.commit()


def get_days():

    return cursor.execute(
        "SELECT * FROM calendar"
    ).fetchall()


def reserve(day, person, color):

    cursor.execute(
        "INSERT INTO calendar VALUES(?,?,?)",
        (day, person, color)
    )

    conn.commit()


def remove(day):

    cursor.execute(
        "DELETE FROM calendar WHERE day=?",
        (day,)
    )

    conn.commit()


def create_request(day, sender, receiver):

    cursor.execute("""

    INSERT INTO requests(
    day,
    sender,
    receiver,
    status
    )

    VALUES(?,?,?,'pending')

    """,(day,sender,receiver))

    conn.commit()


def get_requests(person):

    return cursor.execute("""

    SELECT id,day,sender,status

    FROM requests

    WHERE receiver=?
    AND status='pending'

    """,(person,)).fetchall()


def accept(req):

    cursor.execute("""

    UPDATE requests

    SET status='accepted'

    WHERE id=?

    """,(req,))

    conn.commit()


def reject(req):

    cursor.execute("""

    UPDATE requests

    SET status='rejected'

    WHERE id=?

    """,(req,))

    conn.commit()
