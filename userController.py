import pandas as pd
import sqlite3


conn=sqlite3.connect('data.db',check_same_thread=False)
c=conn.cursor()

def create():
    c.execute('CREATE TABLE IF NOT EXISTS coldDrinks (time TEXT, name TEXT, count INTEGER)')

def insert(time,name,count):
    c.execute('INSERT INTO coldDrinks (time, name, count) VALUES (?,?,?)',(time, name, count))
    conn.commit()

def read():
    c.execute("SELECT * FROM pragma_table_info('coldDrinks')")
    ind=[entry[1] for entry in c.fetchall()]
    c.execute('SELECT * FROM coldDrinks')
    values=c.fetchall()
    data= pd.DataFrame(values,columns=ind)
    return data

def count_drinks():
    c.execute("SELECT name, sum(count) from coldDrinks GROUP BY name")
    values=c.fetchall()
    data=pd.DataFrame(values,columns=["name","count"])
    return data

def csvformat(data):
    df = pd.DataFrame(data)
    df.to_csv('coldDrinks.csv')

def excelformat(data):
    df = pd.DataFrame(data)
    writer = pd.ExcelWriter('coldDrinks.xlsx')
    df.to_excel(writer)
    writer.save()