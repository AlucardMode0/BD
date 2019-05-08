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
import re


# autentificare
ID='0'
Camera='1'

#inregistrare casa

Casa_Str=''
Casa_nr=''
Casa_nr_poarta=''
Casa_nr_camere=''
#inregistrare bloc

Bloc_Str=''
Bloc_nr=''
Bloc_bl=''
Bloc_et=''
Bloc_ap=''
Bloc_nr_camere=''

NR_CAMERE=0

def replaceAll(file,senzor):
    global ID
    global Camera
    global NR_CAMERE

    while (1):

        list = []
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        cur.execute("select count(camera_id) from (select * from camera order by casa_id desc) where casa_id={0}".format(int(ID)));
        for result in cur:
            NR_CAMERE =result[0]
            #print (NR_CAMERE)
        cur.execute(
            "select 'new Date'||TO_CHAR(add_months(isz.data,-1), '(YYYY, MM, DD, HH24, MI, SS)') ,isz.value from istoric_senzori isz,senzori s,camera c,casa x where x.casa_id = c.casa_id and c.camera_id=s.camera_id and s.id_senzori=isz.id_senzori and x.casa_id={0} and c.camera_id like'%{1}' and s.tip='{2}' order by isz.data".format(int(ID),int(Camera),senzor))
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
        f=open(file,'w')
        f.write("""// Themes begin
                    am4core.useTheme(am4themes_animated);
                    // Themes end
                    
                    // Create chart instance
                    var chart = am4core.create("%s", am4charts.XYChart);
                    
                    // Add data
                    chart.data = generateChartData();
                    
                    // Create axes
                    var dateAxis = chart.xAxes.push(new am4charts.DateAxis());
                    dateAxis.renderer.minGridDistance = 50;
                    
                    var valueAxis = chart.yAxes.push(new am4charts.ValueAxis());
                    
                    // Create series
                    var series = chart.series.push(new am4charts.LineSeries());
                    series.dataFields.valueY = "visits";
                    series.dataFields.dateX = "date";
                    series.strokeWidth = 2;
                    series.minBulletDistance = 10;
                    series.tooltipText = "{valueY}";
                    series.tooltip.pointerOrientation = "vertical";
                    series.tooltip.background.cornerRadius = 20;
                    series.tooltip.background.fillOpacity = 0.5;
                    series.tooltip.label.padding(12,12,12,12)
                    
                    // Add scrollbar
                    chart.scrollbarX = new am4charts.XYChartScrollbar();
                    chart.scrollbarX.series.push(series);
                    
                    // Add cursor
                    chart.cursor = new am4charts.XYCursor();
                    chart.cursor.xAxis = dateAxis;
                    chart.cursor.snapToSeries = series;
                    function generateChartData() {
                    var chartData = [%s];
                        return chartData;
                    }""" %(senzor,string)
                )
        time.sleep(1)


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
    global NR_CAMERE

    x=0
    str = request.form['aut']
    if 'aut' in str:
        ID = request.form['ID']
        Camera=request.form['Camera']
        try :
            x = int(ID)
            x = int(Camera)
            connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
            cur = connection.cursor()
            cur.execute(
                "select count(camera_id) from (select * from camera order by casa_id desc) where casa_id={0}".format(
                    int(ID)));
            for result in cur:
                NR_CAMERE = result[0]
            cur.close()
            connection.close()
        except:
            return render_template("home.html", error='ID-ul sau Camera nu sunt "numere intregi" pentru baza date')
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        cur.execute(
            "select count(casa_id) from casa where casa_id = {0}".format(ID))
        for result in cur:
            if(result[0]):
                return redirect('camera')
                return render_template("Camera", last_updated=dir_last_updated('static'),wait='wait')
            else:
                return render_template("home.html", error='Casa nu se afla in baza de date!')
        cur.close()
        connection.close()
    # inregistrare casa


    global Casa_Str
    global Casa_nr
    global Casa_nr_poarta
    global Casa_nr_camere
    # inregistrare bloc
    if str == 'casa_new':
        Casa_Str = request.form['casa_Str']
        Casa_nr = request.form['casa_nr']
        Casa_nr_poarta = request.form['casa_nr_poarta']
        Casa_nr_camere = request.form['casa_nr_camere']
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        try:
            x = int(Casa_nr_camere)
            if x>9:
                return render_template("home.html", error1='casa poate avea maxim 9 camere')
            if x<1:
                return render_template("home.html", error1='casa poate avea minim 1 camera')
        except:
            return render_template("home.html", error1='Camera trebuie sa fie numar "intreg" pentru baza date')
        cur = connection.cursor()
        new_cur = connection.cursor()
        cur.execute(
            "Insert into casa values(casa_id_seq.nextval,'{0},nr. {1} ,poarta {2} ,nr_camera {3}')".format(Casa_Str,
                                                                                                           Casa_nr,
                                                                                                           Casa_nr_poarta,
                                                                                                           Casa_nr_camere))
        for i in range(1, int(Casa_nr_camere) + 1):
            cur.execute(
                "insert into camera (camera_id,metri_patrati,casa_id)select max(casa_id) || '_{0}', null, max(casa_id) from casa".format(
                    i))
            cur.execute("select camera_id from (select * from camera order by casa_id desc) where rownum <{0}".format(
                int(Casa_nr_camere) + 1));
        for result in cur:
            new_cur.execute(
                "Insert into senzori values (casa_id_seq.nextval,'trafic',0,TO_DATE('1/1/2000 01:00:20','DD/MM/YY HH:MI:SS'),'{0}')  ".format(
                    result[0]))
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
                ID = result[0]
                Camera = 1
                return render_template("Camera.html", last_updated=dir_last_updated('static'),  error='ID-ul casei este {0}'.format(result[0]), wait=' to create data')
        cur.close()
        new_cur.close()
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
        try:
            x = int(Bloc_nr_camere)
            if x > 9:
                return render_template("home.html", error1='casa poate avea maxim 9 camere')
            if x<1:
                return render_template("home.html", error1='casa poate avea minim 1 camera')
        except:
            return render_template("home.html", error1='Camera trebuie sa fie numar "intreg" pentru baza date')
        connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
        cur = connection.cursor()
        new_cur=connection.cursor()
        cur.execute("Insert into casa values(casa_id_seq.nextval,'{0},nr. {1},bl. {2},sc. {3},et. {4},ap. {5}')".format(Bloc_Str,Bloc_nr,Bloc_bl,Bloc_et,Bloc_ap,Bloc_nr_camere))
        for i in range (1,int(Bloc_nr_camere)+1):
            cur.execute("insert into camera (camera_id,metri_patrati,casa_id)select max(casa_id) || '_{0}', null, max(casa_id) from casa".format(i))
        cur.execute("select camera_id from (select * from camera order by casa_id desc) where rownum <{0}".format(int(Bloc_nr_camere)+1));
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
                return render_template("Camera.html", last_updated=dir_last_updated('static'),  error='ID-ul casei este {0}'.format(result[0]),wait=' to create data')
        cur.close()
        new_cur.close()
        connection.close()
    return render_template("Camera.html", last_updated=dir_last_updated('static'),wait='wait')


@app.route("/camera")
def salvador():
    global Camera
    global NR_CAMERE
    if int(Camera)>int (NR_CAMERE):
        return render_template("Camera.html", last_updated=dir_last_updated('static'),nr_camere="Casa are doar {0} camere si va aflati pe camera {1}".format(NR_CAMERE,Camera))
    else:
        return render_template("Camera.html", last_updated=dir_last_updated('static'))
    return render_template("Camera.html", last_updated=dir_last_updated('static'))

@app.route("/camera", methods=['POST'])
def salvador1():
    global Camera
    global NR_CAMERE
    try:
        Camera=request.form['Camera_id']
        if int(Camera)>int (NR_CAMERE):
            return render_template("Camera.html", last_updated=dir_last_updated('static'),nr_camere="Casa are doar {0} camere si va aflati pe camera {1}".format(NR_CAMERE,Camera))
        else:
            return render_template("Camera.html", last_updated=dir_last_updated('static'))
    except :
        action = request.form['action']

        if ('delete') in action:
            start = request.form['start']
            stop = request.form['stop']
            if(re.match('(\d\d-\d\d-\d\d\d\d)',str(start)) and (re.match('(\d\d-\d\d-\d\d\d\d)',str(stop)))):
                connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
                cur = connection.cursor()
                cur1 = connection.cursor()
                cur.execute(
                    "select distinct i.id_senzori from casa c, camera x, senzori z , istoric_senzori i where c.casa_id=x.casa_id and x.camera_id=z.camera_id and z.id_senzori =i.id_senzori and x.camera_id='{0}_{1}' and i.tip='{2}' ".format(int(ID),Camera,action.split('_')[1]));
                for result in cur:

                    cur1.execute("delete from istoric_senzori  where  id_senzori={2} and data BETWEEN To_date('{0}','dd-mm-yyyy')  AND To_date('{1}','dd-mm-yyyy')".format(start,stop,result[0]))
                cur.execute('commit')
                cur.close()
                cur1.close()
                connection.close()
                return render_template("Camera.html", last_updated=dir_last_updated('static'), )
            else:
                return render_template("Camera.html", last_updated=dir_last_updated('static'),error='format data invalid' )
        if ('add') in action:
                value =request.form['valoare']
                try :
                    x= int (value)
                    connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
                    cur = connection.cursor()
                    cur1 = connection.cursor()
                    print(1)
                    cur.execute(
                        "select distinct z.id_senzori from casa c, camera x, senzori z , istoric_senzori i where c.casa_id=x.casa_id and x.camera_id=z.camera_id and z.id_senzori =i.id_senzori(+) and x.camera_id='{0}_{1}' and z.tip='{2}' ".format(
                            int(ID), Camera, action.split('_')[1]));
                    print(2)
                    for result in cur:
                        print(3)
                        cur1.execute("insert into istoric_senzori Values('{0}',{1},SYSDATE,{2})".format(action.split('_')[1], value,result[0]))
                        print (result[0])
                        print(4)
                        cur1.execute("Update senzori set Value={0},Data=SYSDATE  where id_senzori={1}".format(value,result[0]))
                    print(5)
                    cur.execute('commit')
                    print(6)
                    cur.close()
                    cur1.close()
                    connection.close()
                    return render_template("Camera.html", last_updated=dir_last_updated('static'), )
                except:
                    return render_template("Camera.html", last_updated=dir_last_updated('static'),
                                           error='valoare invalida')

if __name__ == "__main__":
    Thread(target=replaceAll, args=("static/trafic.js", 'trafic',)).start()
    Thread(target=replaceAll, args=("static/electricitate.js", 'electricitate',)).start()
    Thread(target=replaceAll, args=("static/apa.js", 'apa',)).start()
    Thread(target=replaceAll, args=("static/gaz.js", 'gaz',)).start()
    Thread(target=replaceAll, args=("static/lumina.js", 'lumina',)).start()
    Thread(target=replaceAll, args=("static/temperatura.js", 'temperatura',)).start()
    Thread(target=replaceAll, args=("static/zgomot.js", 'zgomot',)).start()

    app.run()
