import cx_Oracle
import calendar
import datetime
import threading
import os
from random import randint
from flask import Flask,  request, render_template
import fileinput
import sys
import time
from threading import Thread


connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
cur = connection.cursor()
cur.execute('select * from senzori')
for result in cur:
    print(result)
cur.close()
connection.close()

Casa= ''
locatie= ''


def replaceAll(file, searchExp, replaceExp):
    while (1):
        for line in fileinput.input(file, inplace=1):
            if searchExp in line:
                line = line.replace(line, replaceExp)
            sys.stdout.write(line)
        time.sleep(0.5)


def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
               for root_path, dirs, files in os.walk(folder)
               for f in files))

app = Flask(__name__)
@app.route('/')
def my_form():
    return render_template('home.html')

@app.route('/', methods=['POST'])
def my_form_post():
    global Casa
    global locatie
    ID = request.form['ID']
    Casa = ID.upper()
    adresa = request.form['adresa']
    locatie = adresa.upper()
    print (Casa,locatie)
    return render_template("Camera.html", last_updated=dir_last_updated('static'))

@app.route("/camera")
def salvador():
    return render_template("Camera.html", last_updated=dir_last_updated('static'))
if __name__ == "__main__":
    list = []
    connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
    cur = connection.cursor()
    cur.execute('select data,value from senzori order by data asc')
    for result in cur:
        dict = {"date": "date", "visits": 0}
        dict["date"] = str(result[0])
        dict["visits"] = result[1] + 23
        list.append(dict)
    cur.close()
    connection.close()
    Thread(target=replaceAll,
           args=("static/Charts.js", 'var chartData = ', 'var chartData = {0};\n'.format(list))).start()
    app.run()
