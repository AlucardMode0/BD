import cx_Oracle

from random import randint
connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
cur = connection.cursor()
for i in range (0,2000 ):
    cur.execute("Insert into senzori values({0},'temp',{0},TO_DATE('{1}/{4}/{2} {5}:{3}:00','DD/MM/YY HH:MI:SS'),'41_1')".format(i,randint(1,11),randint(2014,2018),randint(0,59),randint(1,11),randint(1,12)))
    cur.execute("commit");
cur.close()
connection.close()
'''
import ast
import sys
import fileinput
def replaceAll(file):
    list = []
    connection = cx_Oracle.connect('system/PentaKill11@localhost:1521/xe')
    cur = connection.cursor()
    cur.execute(
        "select 'new Date'||TO_CHAR(data, '(YYYY, MM, DD, HH24, MI, SS)') ,value from senzori order by data asc")
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

replaceAll("static/Charts.js")
'''