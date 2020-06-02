#!/usr/bin/python3
#coding: utf-8

from datetime import datetime
import time
import sqlite3
import serial

conn = sqlite3.connect("/opt/camara_barometrica/registro.db",timeout=10)
porta = serial.Serial("/dev/ttyACM0",57600)
resposta = " "

def teste_s():
    msg = b'<?>'
    porta.write(msg) # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    if (str(resposta) == "b'<?>\\r\\n'"):
        print("Serial OK")
    else:
        print("Serial sem resposta")
    #msg = porta.readline() #limpar buffer
    #print(msg)
    return resposta

def send_all_data():
    porta.write(b'<a>') # Escrever dados na porta serial
    resposta = str(porta.readline()) # Receber dados na porta serial
    resposta = list(resposta.replace("b'<a;","").replace(">\\r\\n'","").split(";"))
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM dinamica WHERE id = 1;""")
    reg = cursor.fetchall()
    conn.close
    # Conectar ao banco de dados
    cursor = conn.cursor()
    # inserir dados na tabela
    # <a;pressao;temperatura;UR;pwmValvulaPressao;pwmValvulaVacuo;statusBomba;statusPid;setpoint>
    cursor.execute("""INSERT INTO medidas (nome, pressao, temperatura, UR, pwm_valvula_pressao, pwm_valvula_vacuo, status_bomba, status_pid, setpoint, estado, data_registro) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", ( reg[0][1], float(resposta[0]), float(resposta[1]), float(resposta[2]), int(resposta[3]), int(resposta[4]), int(resposta[5]), int(resposta[6]), float(resposta[7]), int(reg[0][12]), str(datetime.today())))
    conn.commit()
    conn.close
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET pressao = ?, temperatura = ?, UR = ?, pwm_valvula_pressao = ?, pwm_valvula_vacuo = ?, status_bomba = ?, status_pid = ?, setpoint = ? WHERE id = 1""", (float(resposta[0]), float(resposta[1]), float(resposta[2]), int(resposta[3]), int(resposta[4]), int(resposta[5]), int(resposta[6]), float(resposta[7])))
    conn.commit()
    conn.close
    print("Parametros gravados no banco de dados " + str(datetime.now()))
    return resposta
 
        

def control_air_pump(acionar_bomba):
    if (acionar_bomba):
        porta.write(b'<b;1>') # Escrever dados na porta serial desligar bomba
    else:
        porta.write(b'<b;0>') # Escrever dados na porta serial ligar bomba
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def set_pwm_pressure_valve(pwm_p):
    porta.write(b'<c;%b>' % str(pwm_p).encode('ascii','ignore')) # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def set_pwm_vacuum_valve(pwm_v):
    porta.write(b'<d;%b>' % str(pwm_v).encode('ascii','ignore')) # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def send_pressure_data():
    porta.write(b'<e>') # Escrever dados na porta serial
    resposta = str(porta.readline()) # Receber dados na porta serial
    resposta = list(resposta.replace("b'<e;","").replace(">\\r\\n'","").split(";"))
    return resposta

def enable_pid(acionar_pid):
    if (acionar_pid):
        porta.write(b'<f;1>') # Escrever dados na porta serial desligar pid
    else:
        porta.write(b'<f;0>') # Escrever dados na porta serial ligar pid
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def update_setpoint(setpoint):
    porta.write(b'<g;%b>' % str(setpoint).encode('ascii','ignore')) # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def set_pid_parameters(p_kp, p_ki, p_kd):
    msg = '<h;{:.4f};{:.4f};{:.4f}>'.format(p_kp,p_ki,p_kd)
    porta.write(msg.encode('ascii','ignore')) # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    print(resposta)
    return resposta

def get_pid_parameters():
    porta.write(b'<i>') # Escrever dados na porta serial
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def set_active_valve(acionar_valvula):
    if (acionar_valvula):
        porta.write(b'<j;1>') # Escrever dados na porta serial desligar pid
    else:
        porta.write(b'<j;0>') # Escrever dados na porta serial ligar pid
    resposta = porta.readline() # Receber dados na porta serial
    return resposta

def set_valvula(erro):
    if erro <= -5 :
        set_pwm_vacuum_valve(0)
        set_active_valve(False)
        set_pid_parameters(40.0, 1, 0.0)
        return "Pressão"
    elif erro <= 0 :
        set_pwm_vacuum_valve(0)
        set_active_valve(False)
        set_pid_parameters(30.0, 1, 0.0)
        return "Pressão"
    elif erro >= 5 :
        set_pwm_pressure_valve(0)
        set_active_valve(True)
        set_pid_parameters(-40.0, -1.0, 0.0)
        return "Pressão"
    else:
        set_pwm_pressure_valve(0)
        set_active_valve(True)
        set_pid_parameters(-30.0, -1.0, 0.0)
        return "Vacuo"


def set_valvula_pressao(erro):
    set_pwm_vacuum_valve(0)
    set_active_valve(False)
    if erro <= -0.25 :
        return set_pid_parameters(50.0, 1.0, 0.0)
    else:
        return set_pid_parameters(30.0, 1.0, 0.0)

def set_valvula_vacuo(erro):
    set_pwm_pressure_valve(0)
    set_active_valve(True)
    if erro >= 0.25 :
        return set_pid_parameters(-50.0, -1.0, 0.0)
    else:
        return set_pid_parameters(-30.0, -1.0, 0.0)

# Não utulizado
def set_valvula_pressao_baixa(erro):
    set_active_valve(False)
    return set_pid_parameters(1.0, 1.0, 0.0)

def set_valvula_pressao_alto(erro):
    set_active_valve(False)
    return set_pid_parameters(99.0, 99.0, 0.0)

def set_valvula_vacuo_baixa(erro):
    set_pwm_pressure_valve(0)
    set_active_valve(True)
    return set_pid_parameters(-1.0, -1.0, 0.0)

def set_valvula_vacuo_alto(erro):
    set_pwm_pressure_valve(0)
    set_active_valve(True)
    return set_pid_parameters(-99.0, -99.0, 0.0)

'''
Rotina de Teste

while True:
    print(teste_s())
    print(send_all_data())
    print(control_air_pump(False))
    print(set_pwm_pressure_valve(500))
    print(set_pwm_vacuum_valve(300))
    print(send_pressure_data())
    print(enable_pid(False))
    print(update_setpoint(958.4))
    print(set_pid_parameters(1.12345,345.12,0))
    print(get_pid_parameters())
    time.sleep(5)
'''