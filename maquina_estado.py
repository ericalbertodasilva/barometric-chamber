#!/usr/bin/python3
#coding: utf-8

import time
import sqlite3
from com_arduino import *
from manipulador import *
from datetime import datetime



estado = 0
inicio = 0
while True:
    try:
        if inicio == 0 :
            update_setpoint(950)
            inicio = 1
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM dinamica WHERE id = 1;""")
        reg = cursor.fetchall()
        conn.close
        agora = datetime.today()
        agora_s = agora.timestamp()
        log_maquina = open("maquina.txt" , "a+")
        log_maquina.write(str(reg)+ " " + str(datetime.now()) +"\n")
        log_maquina.close()
        #print(reg)
        erro = reg[0][13] - reg[0][20]
        if reg[0][12] == 0:
            if ((agora_s > reg[0][3]) and (reg[0][3] > 0)):
                cursor = conn.cursor()
                cursor.execute("""UPDATE dinamica SET estado = 1 WHERE id = 1""")
            if (int(reg[0][19])>0):
                set_valvula(erro)
            print("Estado 0")
        elif reg[0][12] == 1:
            cursor = conn.cursor()
            p_inicial =send_pressure_data()
            f_atingir_ref = (reg[0][4] - float(p_inicial[0])) / (reg[0][5] - reg[0][3])  #(p_ref - p_inicial) / t_inicial
            f_atingir_ensaio = (reg[0][8] - reg[0][4]) / (reg[0][9] - reg[0][7]) #(p_ref - p_ensaio) / t_atingir_ensaio
            print (f_atingir_ref)
            print(f_atingir_ensaio)
            cursor.execute("""UPDATE dinamica SET p_inicial = ?, f_atingir_ref = ?, f_atingir_ensaio = ?, estado = 2, status_bomba = 1, status_pid = 1 WHERE id = 1""", (float(p_inicial[0]), float(f_atingir_ref), float(f_atingir_ensaio)))
            conn.commit()
            control_air_pump(True)
            enable_pid(True)
            update_setpoint(float(p_inicial[0]))
            print("Estado 1")
        elif reg[0][12] == 2:
            if reg[0][2] <= reg[0][20]:
                set_valvula_pressao(erro)
                print(str(reg[0][2])+" Comparando "+str(reg[0][20])+" V Pressão "+str(reg[0][12]))
            else:
                set_valvula_vacuo(erro)
                print(str(reg[0][2])+" Comparando "+str(reg[0][20])+" V Vacuo "+str(reg[0][12]))
            cursor = conn.cursor()
            setpoint = (agora_s - reg[0][3]) * reg[0][6] + reg[0][2]
            update_setpoint(setpoint)
            cursor.execute("""UPDATE dinamica SET setpoint = ? WHERE id = 1""",(setpoint,))
            conn.commit()
            if (agora_s >= reg[0][5]):
                cursor = conn.cursor()
                cursor.execute("""UPDATE dinamica SET estado = 3 WHERE id = 1""")
                conn.commit()
            print("Estado 2")
        elif reg[0][12] == 3:
            cursor = conn.cursor()
            update_setpoint(reg[0][4])
            cursor.execute("""UPDATE dinamica SET setpoint = ? WHERE id = 1""",(reg[0][4],))
            conn.commit()
            if (agora_s >= reg[0][7]):
                cursor = conn.cursor()
                cursor.execute("""UPDATE dinamica SET estado = 4 WHERE id = 1""")
                conn.commit()
            print("Estado 3")
        elif reg[0][12] == 4:
            if reg[0][2] <= reg[0][20]:
                set_valvula_pressao(erro)
                print(str(reg[0][2])+" Comparando "+str(reg[0][20])+" V Pressão " +str(reg[0][12]) + "erro " + str(erro))
            else:
                set_valvula_vacuo(erro)
                print(str(reg[0][2])+" Comparando "+str(reg[0][20])+" V Vacuo " +str(reg[0][12]) + "erro " + str(erro))
            cursor = conn.cursor()
            setpoint = (agora_s - reg[0][7]) * reg[0][10] + reg[0][4]
            update_setpoint(setpoint)
            cursor.execute("""UPDATE dinamica SET setpoint = ? WHERE id = 1""",(setpoint,))
            conn.commit()
            if (agora_s >= reg[0][9]):
                cursor = conn.cursor()
                cursor.execute("""UPDATE dinamica SET estado = 5 WHERE id = 1""")
                conn.commit()
            print("Estado 4")
        elif reg[0][12] == 5:
            cursor = conn.cursor()
            update_setpoint(reg[0][8])
            cursor.execute("""UPDATE dinamica SET setpoint = ? WHERE id = 1""",(reg[0][8],))
            conn.commit()
            if (agora_s >= reg[0][11]):
                gravar_csv(reg[0][1])
                plot_graf(reg[0][1])
                # Zerando parametros
                cursor.execute("""UPDATE dinamica SET nome = 'parado', t_inicial = 0.0, p_ref = 0.0, t_atingir_ref = 0.0, f_atingir_ref = 0.0 , t_estavel = 0.0, p_ensaio = 0.0, t_atingir_ensaio = 0.0, f_atingir_ensaio = 0.0, t_final = 0.0, estado = 0, status_bomba = 0, status_pid = 0 WHERE id = 1""")
                conn.commit()
                control_air_pump(False)
                enable_pid(False)
                update_setpoint(reg[0][2])
            print("Estado 5")
        elif reg[0][12] == 6: # Estador Cancelar Ensaio
            control_air_pump(False)
            enable_pid(False)
            set_pwm_pressure_valve(0)
            set_pwm_vacuum_valve(0)
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET t_inicial = 0.0, p_ref = 0.0, t_atingir_ref = 0.0, f_atingir_ref = 0.0 , t_estavel = 0.0, p_ensaio = 0.0, t_atingir_ensaio = 0.0, f_atingir_ensaio = 0.0, t_final = 0.0, estado = 0, status_bomba = 0, status_pid = 0 WHERE id = 1""")
            conn.commit()
            update_setpoint(reg[0][2])
            print("Estado 6")
        elif reg[0][12] == 7: # Estador ligar Bomba
            print(control_air_pump(True))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0, status_bomba = 1 WHERE id = 1""")
            conn.commit()
            print("Estado 7")
        elif reg[0][12] == 8: # Estador Desligar Bomba
            print(control_air_pump(False))
            update_setpoint(940)
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0, status_bomba = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 8")
        elif reg[0][12] == 9: # Estador Ligar PID
            print(enable_pid(True))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0, status_pid = 1 WHERE id = 1""")
            conn.commit()
            print("Estado 9")
        elif reg[0][12] == 10: # Estador Deligar PID
            print(enable_pid(False))
            update_setpoint(940)
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0, status_pid = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 10")
        elif reg[0][12] == 11: # Estador Atualizar PID
            cursor = conn.cursor()
            cursor.execute("""SELECT * FROM pid WHERE id=(SELECT MAX(id) FROM pid);""")
            reg = cursor.fetchall()
            print(set_pid_parameters(reg[-1][1], reg[-1][2], reg[-1][3]))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 11")
        elif reg[0][12] == 12: # Estador Gravar posição válvula pressão
            print(reg[0][16])
            print(set_pwm_pressure_valve(reg[0][16]))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 12")
        elif reg[0][12] == 13: # Estador Gravar posição válvula vacuo
            print(reg[0][17])
            print(set_pwm_vacuum_valve(reg[0][17]))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 13")
        elif reg[0][12] == 14: # Atualizar setpoint
            print(reg[0][20])
            print(update_setpoint(reg[0][20]))
            cursor = conn.cursor()
            cursor.execute("""UPDATE dinamica SET estado = 0 WHERE id = 1""")
            conn.commit()
            print("Estado 14")
        else:
            print("Estados não existe") 
        conn.close
        send_all_data()
    except:
        print("Problemas com Maquida de Estado")
    time.sleep(3)