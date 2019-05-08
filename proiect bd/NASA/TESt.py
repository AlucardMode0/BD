import cx_Oracle
import calendar
import datetime
import threading
import os
from random import randint
from flask import Flask,  request, render_template,redirect
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
# autentificare
ID='0'
Camera='1'

#inregistrare casa

Casa_Str=''
Casa_nr=''
Casa_nr_camere=''
#inregistrare bloc

Bloc_Str=''
Bloc_nr=''
Bloc_bl=''
Bloc_et=''
Bloc_ap=''
Bloc_nr_camere=''

def replaceAll(file):
    global ID
    global Camera
    while (1):
        list = []
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        cur.execute(
            "select 'new Date'||TO_CHAR(isz.data, '(YYYY, MM, DD, HH24, MI, SS)') ,isz.value from istoric_senzori isz,senzori s,camera c,casa x where x.casa_id = c.casa_id and c.camera_id=s.camera_id and s.id_senzori=isz.id_senzori and x.casa_id={0} and c.camera_id like'%{1}' and s.tip='trafic' order by isz.data".format(int(ID),int(Camera)))
        for result in cur:
            dict = {"date": 0, "visits": 0}
            dict["date"] = result[0]
            dict["visits"] = result[1]
            list.append(dict)
        cur.close()
        connection.close()
        string = ''
        for i in list:
            string = string + "{'date': " + i['date'] + " ,'visits': " + str(i['visits']) + '},'
        for line in fileinput.input(file, inplace=1):
            if 'var chartData = ' in line:
                line = line.replace(line, 'var chartData = [{0}];\n'.format(string))
            sys.stdout.write(line)
        time.sleep(10)


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
    global ID
    global Camera

    str = request.form['aut']
    if 'aut' in str:
        ID = request.form['ID']
        Camera=request.form['Camera']
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        cur.execute(
            "select count(casa_id) from casa where casa_id = {0}".format(ID))
        for result in cur:
            if(result[0]):
                return render_template("Camera.html", last_updated=dir_last_updated('static'))
            else:
                return render_template("home.html", error='Casa nu se afla in baza de date!')
        cur.close()
        connection.close()
    # inregistrare casa


    global Casa_Str
    global Casa_nr
    global Casa_nr_camere
    # inregistrare bloc
    if str == 'casa_new':
        Casa_Str  = request.form['casa_Str']
        Casa_nr = request.form['casa_nr']
        Casa_nr_camere = request.form['Casa_nr_camere']
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        cur.execute(
            "select max(casa_id)from casa;")
        for result in cur:
            if (result[0]):
                return render_template("Camera.html", last_updated=dir_last_updated('static'),error=result[0])
        cur.close()
        connection.close()

    global Bloc_Str
    global Bloc_nr
    global Bloc_bl
    global Bloc_et
    global Bloc_ap
    global Bloc_nr_camere
    if str =='bloc_new':
        Bloc_Str= request.form['bloc_Str']
        Bloc_nr= request.form['bloc_nr']
        Bloc_bl= request.form['bloc_bl']
        Bloc_et= request.form['bloc_et']
        Bloc_ap= request.form['bloc_ap']
        Bloc_nr_camere= request.form['bloc_nr_camere']
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        new_cur=connection.cursor()
        cur.execute("Insert into casa values(casa_id_seq.nextval,'{0},nr. {1},bl. {2},sc. {3},et. {4},ap. {5}')".format(Bloc_Str,Bloc_nr,Bloc_bl,Bloc_et,Bloc_ap,Bloc_nr_camere))
        for i in range (1,int(Bloc_nr_camere)+1):
            cur.execute("insert into camera (camera_id,metri_patrati,casa_id)select max(casa_id) || '_{0}', null, max(casa_id) from casa".format(i))
        cur.execute("select camera_id from camera");
        for result in cur:
            new_cur.execute("Insert into senzori values (casa_id_seq.nextval,'trafic',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'apa',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'electricitate',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'lumina',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'temperatura',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'gaz',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'zgomot',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
        cur.execute("commit")
        cur.execute("select max(casa_id) from casa")

        for result in cur:
            if (result[0]):
                ID=result[0]
                Camera=1
                return render_template("Camera.html", last_updated=dir_last_updated('static'), error=result[0])
        cur.close()
        new_cur.close()
        connection.close()
    return render_template("Camera.html", last_updated=dir_last_updated('static'))


@app.route("/camera")
def salvador():
    return render_template("Camera.html", last_updated=dir_last_updated('static'))
if __name__ == "__main__":

    Thread(target=replaceAll,args=("static/trafic.js",)).start()
    app.run()
