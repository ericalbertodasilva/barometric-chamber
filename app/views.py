from flask import render_template, request, redirect, url_for, jsonify, Response, stream_with_context, send_file
from app.models import Ensaios, Medidas, Pid, Manual, Dinamica
from app import app, db
import time
import io
import sqlite3
from datetime import *
from manipulador import *


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/monitorar')
def monitorar():
    return render_template('monitorar.html')

@app.route('/controle')
def controle():
    return render_template('controle.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/graficos')
def graficos():
    return render_template('graficos.html')

@app.route('/grafico_pressao')
def grafico_pressao():
    return render_template('grafico_pressao.html')

@app.route('/_get_ensaios_nomes', methods=['POST',])
def _get_ensaios_nomes():
    try:
        resultado = Ensaios.query.all()
        t = {}
        for x in range(len(resultado)):
            t.update({resultado[x].nome:resultado[x].nome})
        return jsonify(t)
    except:
        return render_template('controle.html')

@app.route('/_get_ensaio_escolhido', methods=['POST',])
def _get_ensaio_escolhido():
    try:
        nome = request.values["nome"]
        resultado = Ensaios.query.filter(Ensaios.nome == str(nome)).first()
        print(resultado)
        t = {}
        t.update({"nome":resultado.nome})
        t.update({"pressao_referencia":resultado.pressao_referencia})
        t.update({"tempo_atingir_referencia":resultado.tempo_atingir_referencia})
        t.update({"tempo_estavel_referencia":resultado.tempo_estavel_referencia})
        t.update({"pressao_de_ensaio":resultado.pressao_de_ensaio})
        t.update({"tempo_atingir_ensaio":resultado.tempo_atingir_ensaio})
        t.update({"ativacao_data":resultado.ativacao_data})
        t.update({"ativacao_hora":resultado.ativacao_hora})
        t.update({"desativacao_data":resultado.desativacao_data})
        t.update({"desativacao_hora":resultado.desativacao_hora})
        return jsonify(t)
    except:
        return render_template('controle.html')

@app.route('/_get_monitor', methods=['POST',])
def _get_monitor():
    try:
        resultado = Dinamica.query.first()
        t = {}
        t.update({"nome":resultado.nome})
        t.update({"estado":resultado.estado})
        t.update({"pressao":resultado.pressao})
        t.update({"temperatura":resultado.temperatura})
        t.update({"UR":resultado.UR})
        t.update({"pwm_valvula_pressao":resultado.pwm_valvula_pressao})
        t.update({"pwm_valvula_vacuo":resultado.pwm_valvula_vacuo})
        t.update({"status_bomba":resultado.status_bomba})
        t.update({"status_pid":resultado.status_pid})
        t.update({"setpoint":resultado.setpoint})
        resultado2 = Pid.query.all()
        t.update({"kp":resultado2[-1].kp})
        t.update({"kd":resultado2[-1].kd})
        t.update({"ki":resultado2[-1].ki})
        return jsonify(t)
    except:
        return render_template('index.html')

@app.route('/executar', methods=['POST',])
def executar():
    nome = str(request.form['nome']) + "(" + str(datetime.today()).replace(":","-") + ")"
    p_ref = float(request.form['pressao_referencia'])
    ta = float(request.form['tempo_atingir_referencia'])
    tr = float(request.form['tempo_estavel_referencia'])
    p_ensaio = float(request.form['pressao_de_ensaio'])
    te = float(request.form['tempo_atingir_ensaio'])
    atd = str(request.form['ativacao_data'])
    att = str(request.form['ativacao_hora'])
    ded = str(request.form['desativacao_data'])
    det = str(request.form['desativacao_hora'])
    p = Ensaios(nome=nome, pressao_referencia=p_ref, tempo_atingir_referencia=ta, tempo_estavel_referencia=tr,
                pressao_de_ensaio=p_ensaio, tempo_atingir_ensaio=te, ativacao_data=atd, ativacao_hora=att,
                desativacao_data=ded, desativacao_hora=det)
    db.session.add(p)
    db.session.commit()
    # Converte tempo inicial em segundos
    atc=(atd+" "+att)
    at=datetime.strptime(atc, "%Y-%m-%d %H:%M")
    t_inicial=at.timestamp()
    # Converte tempo final em segundos
    dc=(ded+" "+det)
    de=datetime.strptime(dc, "%Y-%m-%d %H:%M")
    t_final=de.timestamp()
    # Tempo real em segudos
    t = datetime.today()
    # Teste para iniciar ensaio
    teste_inicio_ensaio = t.timestamp() - t_inicial
    # calculos dos tempos do ensaio
    t_atingir_ref = t_inicial + ta
    t_estavel = t_atingir_ref + tr
    t_atingir_ensaio = t_estavel + te
    # Atualizar BD tabela Dinamica
    if teste_inicio_ensaio < 0 :
        conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
        cursor = conn.cursor()
        cursor.execute("""UPDATE dinamica SET nome = ?, t_inicial = ?, p_ref = ?, t_atingir_ref = ?, t_estavel = ?, p_ensaio = ?, t_atingir_ensaio = ?, t_final = ?, estado = 0 WHERE id = 1""", (nome, float(t_inicial), float(p_ref), float(t_atingir_ref), float(t_estavel), float(p_ensaio), float(t_atingir_ensaio), float(t_final)))
        conn.commit()
        print("Ensaio programado")
        conn.close()
    else:
        print("Hora iniciar maior que hora atual")
    print("controle")
    return render_template('index.html')

@app.route('/cancelar')
def cancelar():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET nome = 'parado', t_inicial = 0, p_ref = 0, t_atingir_ref = 0, t_estavel = 0, p_ensaio = 0, t_atingir_ensaio = 0, t_final = 0, estado = 6 WHERE id = 1""")
    conn.commit()
    conn.close()
    print("Ensaio Cancelado")
    return render_template('index.html')

@app.route('/criar_ensaio', methods=['POST',])
def criar_ensaio():
    try:
        n = str(request.form['cadastro_nome'])
        pr = int(request.form['cadastro_p_ref'])
        ta = int(request.form['cadastro_t_a_p_ref'])
        tr = int(request.form['cadastro_t_p_ref'])
        pe = int(request.form['cadastro_p_e'])
        te = int(request.form['cadastro_t_a_p_e'])
        atd = str(request.form['cadastro_a_c_d'])
        att = str(request.form['cadastro_a_c_t'])
        ded = str(request.form['cadastro_d_c_d'])
        det = str(request.form['cadastro_d_c_t'])
        p = Ensaios(nome=n, pressao_referencia=pr, tempo_atingir_referencia=ta, tempo_estavel_referencia=tr, pressao_de_ensaio=pe, tempo_atingir_ensaio=te, ativacao_data=atd, ativacao_hora=att, desativacao_data=ded, desativacao_hora=det)
        db.session.add(p)
        db.session.commit()
        return render_template('controle.html')
    except:
        return render_template('cadastro.html')

@app.route('/registrar_pid', methods=['POST',])
def registrar_pid():
    try:
        kp = float(request.form['kp'])
        kd = float(request.form['kd'])
        ki = float(request.form['ki'])
        p = Pid(kp=kp, kd=kd,ki=ki)
        db.session.add(p)
        db.session.commit()
        return render_template('manual.html')
    except:
        return render_template('manual.html')


@app.route('/ligar_bomba', methods=['POST',])
def ligar_bomba():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET estado = 7 WHERE id = 1""")
    conn.commit()
    conn.close()
    print("Ligando Bomba")
    return "ok"

@app.route('/desligar_bomba', methods=['POST',])
def desligar_bomba():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET estado = 8 WHERE id = 1""")
    conn.commit()
    conn.close()
    print("Desligar Bomba")
    return "ok"

@app.route('/ligar_pid', methods=['POST',])
def ligar_pid():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET estado = 9 WHERE id = 1""")
    conn.commit()
    conn.close()
    print("Ligando PID")
    return "ok"

@app.route('/desligar_pid', methods=['POST',])
def desligar_pid():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET estado = 10 WHERE id = 1""")
    conn.commit()
    conn.close()
    print("Desligar PID")
    return "ok"

@app.route('/valvula_pressao', methods=['POST',])
def valvula_pressao():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    ppre = request.values["ppressao"]
    ppre=int(ppre)*10.24
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET  pwm_valvula_pressao = ? , estado = 12 WHERE id = 1""",(int(ppre),))
    print(int(ppre))
    conn.commit()
    conn.close()
    print("Posição da válvula de pressão alterada " + str(ppre))
    return "ok"

@app.route('/valvula_vacuo', methods=['POST',])
def valvula_vacuo():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    pvac = request.values["pvacuo"]
    pvac = int(pvac)*10.24
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET pwm_valvula_vacuo = ? , estado = 13 WHERE id = 1""",(int(pvac),))
    print(int(pvac))
    conn.commit()
    conn.close()
    print("Posição da válvula de vacuo alterada " + str(pvac))
    return "ok"

@app.route('/setpoint', methods=['POST',])
def setpoint():
    conn = sqlite3.connect("/opt/camara_barometrica/registro.db", timeout=10)
    sp = request.values["sp"]
    sp = int(sp)
    cursor = conn.cursor()
    cursor.execute("""UPDATE dinamica SET  setpoint = ? , estado = 14 WHERE id = 1""",(int(sp),))
    print(int(sp))
    conn.commit()
    conn.close()
    print("Setpoint atualizado " + str(sp))
    return "ok"

@app.route('/gerar_grafico_proj', methods=['POST',])
def gerar_grafico_proj():
    nome = request.values["nome"]
    plot_graf(nome)
    return 'ok'

@app.route('/gerar_grafico', methods=['POST',])
def gerar_grafico():
    titulo = request.values["titulo"] 
    nome_x = request.values["nome_x"]
    nome_y = request.values["nome_y"]
    vx = request.values["vx"]
    ylow = float(request.values["ylow"])
    yhigh = float(request.values["yhigh"])
    xlow = datetime.strptime((request.values["xlow"]+':00.00000'), "%Y-%m-%dT%H:%M:%S.%f")
    xhigh = datetime.strptime((request.values["xhigh"]+':00.00000'), "%Y-%m-%dT%H:%M:%S.%f")
    grade = request.values["grade"]
    rr = request.values["rrr"]
    ltam = int(request.values["ltam"])
    htam = int(request.values["htam"])
    xdelta = (xhigh - xlow).total_seconds()
    ydelta = yhigh - ylow
    if ydelta < 0:
        return "Variaveis invalidas, limite y menor maior que o limite y maior"
    elif xdelta > 129600:
        return "Datas invalidas, Maior que 36h"
    elif xdelta < 0:
        return "Variaveis invalidas, data menor maior que a data maior"
    else:
        medidass = Medidas.query.filter(Medidas.data_registro <= xhigh).filter(Medidas.data_registro >= xlow).all()
        plot_graf_perso(titulo, nome_x, nome_y, vx, ylow, yhigh, xlow, xhigh, grade, medidass, rr, ltam, htam)
        gravar_csv_penso(titulo, medidass, rr)
        return 'Gráfico Gerado'
    

@app.route('/<int:rr>/plot.png')
def plot(rr):
    print(rr)
    return send_file(str(rr)+"plot.png", mimetype='image/png')

@app.route('/_get_grafico', methods=['POST',])
def _get_grafico():
    nome = request.values["nome"]
    medidass = Medidas.query.filter(Medidas.nome == str(nome)).filter(Medidas.estado > 0).all()
    j = ""
    pontos = int(len(medidass)/80)
    cont = 0
    for medi in medidass:
        if pontos > cont:
            cont = cont + 1
        else:
            cont = 0
            j = j + str({'data_registro':str(medi.data_registro), 'pressao':str(medi.pressao), 'temperatura':str(medi.temperatura), 'UR':str(medi.UR), 'setpoint':str(medi.setpoint)})
    return "["+ j.replace("}{","} , {").replace("'","\"") + "]"

@app.route('/_get_grafico_ponto', methods=['POST',])
def _get_grafico_ponto():
    data_anterior = datetime.now() + timedelta(hours=-1)
    medidass = Medidas.query.filter(Medidas.data_registro >= data_anterior).all()
    j = str({'data_registro':str(medidass[-1].data_registro), 'pressao':str(medidass[-1].pressao), 'temperatura':str(medidass[-1].temperatura), 'UR':str(medidass[-1].UR), 'setpoint':str(medidass[-1].setpoint)})
    return "["+ j.replace("}{","} , {").replace("'","\"") + "]"