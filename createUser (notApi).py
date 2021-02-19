import sqlite3 as sl

con = sl.connect('site.db')
cur=con.cursor()
obj=cur.execute("INSERT INTO users (name,password) VALUES (?,?)",("test","test"))
con.commit()