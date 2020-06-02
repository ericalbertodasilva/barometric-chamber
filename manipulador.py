#!/usr/bin/python3

from datetime import datetime
import time
import sqlite3
import csv
import matplotlib
import matplotlib.pyplot as plt

#criar graficos
def plot_graf_perso(titulo, nome_x, nome_y, vx, ylow, yhigh, xlow, xhigh, grade, medidass, rr, ltam, htam):
    p1 = []
    t1 = []
    h1 = []
    s1 = []
    d1 = []
    for medi in medidass:
        p1.append(medi.pressao)
        t1.append(medi.temperatura)
        h1.append(medi.UR)
        s1.append(medi.setpoint)
        d1.append(medi.data_registro)
    plt.figure()
    plt.title(titulo)
    plt.ylabel(nome_y)
    plt.xlabel(nome_x)
    plt.rcParams['figure.figsize'] = (ltam, htam)
    if (vx == "Pressão e Setpoint"):
        plt.plot(d1,p1, label='Pressão')
        plt.plot(d1,s1, label='Setpoint')
    elif (vx == "Pressão"):
        plt.plot(d1,p1, label='Pressão')
    elif (vx == "Temperatura"):
        plt.plot(d1,t1, label='Temperatura')
    elif (vx == "Humidade"):
        plt.plot(d1,h1, label='Humidade')
    elif (vx == "Setpoint"):
        plt.plot(d1,s1, label='Setpoint')
    if (grade == "Com grade"):
        plt.grid(True)
    else:
        plt.grid(False)
    plt.ylim([ylow, yhigh])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best')
    plt.savefig("/home/pi/Área de Trabalho/Ensaios/"+rr+"plot.png")
    plt.clf()
    plt.cla()

    
def plot_graf(nome):
    p1 = []
    t1 = []
    h1 = []
    s1 = []
    d1 = []
    try:
        conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""SELECT pressao, temperatura, UR, setpoint, data_registro FROM medidas WHERE nome = ?  AND estado > 0;""" , (nome,))
        reg = cursor.fetchall()
        for p,t,h,s,d in reg:
            p1.append(p)
            t1.append(t)
            h1.append(h)
            s1.append(s)
            d1.append(datetime.strptime(d, "%Y-%m-%d %H:%M:%S.%f"))
        print("Banco de dados OK")
    except:
        print("Ensaio não possui registros")
    plt.figure()
    plt.clf()
    plt.cla()
    plt.plot(d1,p1, label='Pressão')
    plt.xlabel('Tempo') 
    plt.ylabel('mBar')
    plt.title("Gráfico de pressão")
    plt.ylim([940, 960])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best')
    plt.rcParams['figure.figsize'] = (7,7)
    plt.savefig('/home/pi/Área de Trabalho/Ensaios/' + nome + ' pressão.png')
    #plt.figure(2)
    plt.clf()
    plt.cla()
    plt.plot(d1,t1, label='Temperatura')
    plt.xlabel('Tempo') 
    plt.ylabel('°C')
    plt.title("Gráfico de temperatura")
    plt.ylim([15, 40])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best')
    plt.rcParams['figure.figsize'] = (7,7)
    plt.savefig('/home/pi/Área de Trabalho/Ensaios/' + nome + ' temperatura.png')
    #plt.figure(3)
    plt.clf()
    plt.cla()
    plt.plot(d1,h1, label='Humidade')
    plt.xlabel('Tempo') 
    plt.ylabel('%')
    plt.title("Gráfico de humidade")
    plt.ylim([0, 100])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best')
    plt.rcParams['figure.figsize'] = (7,7)
    plt.savefig('/home/pi/Área de Trabalho/Ensaios/' + nome + ' humidade.png')
    #plt.figure(4)
    plt.clf()
    plt.cla()
    plt.plot(d1,p1, label='Pressão')
    plt.plot(d1,s1, label='Setpoint')
    plt.xlabel('Tempo') 
    plt.ylabel('mBar')
    plt.title("Gráfico de pressão")
    plt.ylim([940, 960])
    plt.gcf().autofmt_xdate()
    plt.legend(loc='best')
    plt.rcParams['figure.figsize'] = (7,7)
    plt.savefig('/home/pi/Área de Trabalho/Ensaios/' + nome + ' setpoint.png')

# Gravando aquivo para csv do ensaio
def gravar_csv(nome):
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    nome_arq = '/home/pi/Área de Trabalho/Ensaios/' + nome + '.csv' #+str(datetime.today())
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM medidas WHERE nome = ? and estado > 0;""", (nome,))
    reg = cursor.fetchall()
    with open(nome_arq, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['id', 'nome', 'pressao', 'temperatura', 'UR', 'pwm_valvula_pressao', 'pwm_valvula_vacuo', 'status_bomba', 'status_pid', 'setpoint', 'estado', 'data_registro'])
        for linha in reg:
            spamwriter.writerow(linha)
    print('Arquivo gerado no diretorio: ' + nome_arq)

# Gravando aquivo personalizado csv
def gravar_csv_penso(nome, medidass, rr):
    nome_arq = '/home/pi/Área de Trabalho/Ensaios/' + nome + rr + '.csv'
    with open(nome_arq, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, delimiter=';', quoting=csv.QUOTE_MINIMAL)
        spamwriter.writerow(['pressao', 'temperatura', 'UR', 'setpoint', 'data_registro'])
        for medi in medidass:
            linha = [medi.pressao, medi.temperatura, medi.UR, medi.setpoint, medi.data_registro]
            spamwriter.writerow(linha)
    print('Arquivo gerado no diretorio: ' + nome_arq)