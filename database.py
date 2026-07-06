import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "calendar.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Tabela rezerwacji
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user TEXT,
                  date TEXT,
                  color TEXT,
                  UNIQUE(date))''')
    
    # Tabela próśb o zamianę
    c.execute('''CREATE TABLE IF NOT EXISTS swap_requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  requester TEXT,
                  target_user TEXT,
                  requested_date TEXT,
                  target_date TEXT,
                  status TEXT)''') # status: pending, accepted, rejected
    
    conn.commit()
    conn.close()

def get_bookings():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM bookings", conn)
    conn.close()
    return df

def add_booking(user, date, color):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    try:
        c.execute("INSERT INTO bookings (user, date, color) VALUES (?, ?, ?)", (user, date, color))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    conn.close()
    return success

def delete_booking(date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE date = ?", (date,))
    conn.commit()
    conn.close()

def create_swap_request(requester, target_user, requested_date, target_date):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO swap_requests (requester, target_user, requested_date, target_date, status) VALUES (?, ?, ?, ?, ?)",
              (requester, target_user, requested_date, target_date, 'pending'))
    conn.commit()
    conn.close()

def get_swap_requests(user):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM swap_requests WHERE target_user = ? AND status = 'pending'", conn, params=(user,))
    conn.close()
    return df

def update_swap_status(request_id, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    if status == 'accepted':
        # Pobierz dane prośby
        c.execute("SELECT requester, target_user, requested_date, target_date FROM swap_requests WHERE id = ?", (request_id,))
        req = c.fetchone()
        if req:
            requester, target_user, req_date, target_date = req
            
            # Wykonaj zamianę w bookings
            # 1. Pobierz kolory
            c.execute("SELECT color FROM bookings WHERE date = ?", (req_date,))
            color_req = c.fetchone()[0]
            c.execute("SELECT color FROM bookings WHERE date = ?", (target_date,))
            color_target = c.fetchone()[0]
            
            # 2. Zamień użytkowników i kolory
            c.execute("UPDATE bookings SET user = ?, color = ? WHERE date = ?", (target_user, color_target, req_date))
            c.execute("UPDATE bookings SET user = ?, color = ? WHERE date = ?", (requester, color_req, target_date))
            
    c.execute("UPDATE swap_requests SET status = ? WHERE id = ?", (status, request_id))
    conn.commit()
    conn.close()
