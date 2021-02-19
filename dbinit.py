import sqlite3 as sl

class dbinitClass:
    def __init__(self):
        con = sl.connect('site.db')
        cur=con.cursor()
        cur.execute("""
                 CREATE TABLE IF NOT EXISTS users(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL UNIQUE,
                            password TEXT NOT NULL
                        );
                """)

        cur.execute("""
                 CREATE TABLE IF NOT EXISTS news(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL,
                            source TEXT,
                            tags TEXT,
                            author TEXT NOT NULL,
                            description TEXT,
                            coverImage TEXT,
                            publishedAt INT NOT NULL,
                            main INT NOT NULL

                        );
                """)

        cur.execute("""
                 CREATE TABLE IF NOT EXISTS tokens(
                            id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                            userId TEXT NOT NULL UNIQUE,
                            token TEXT NOT NULL UNIQUE
                        );
                """)
        con.commit()

