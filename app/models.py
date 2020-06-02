from app import db
from datetime import datetime
import time


class Ensaios(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    pressao_referencia = db.Column(db.Integer, nullable=False)
    tempo_atingir_referencia = db.Column(db.Integer, nullable=False)
    tempo_estavel_referencia = db.Column(db.Integer, nullable=False)
    pressao_de_ensaio = db.Column(db.Integer, nullable=False)
    tempo_atingir_ensaio = db.Column(db.Integer, nullable=False)
    ativacao_data = db.Column(db.String(10), nullable=False)
    ativacao_hora = db.Column(db.String(10), nullable=False)
    desativacao_data = db.Column(db.String(10), nullable=False)
    desativacao_hora = db.Column(db.String(10), nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Ensaios {}>'.format(self.id)


class Medidas(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100), nullable=False)
    pressao = db.Column(db.Float, nullable=False)
    temperatura = db.Column(db.Float, nullable=False)
    UR = db.Column(db.Float, nullable=False)
    pwm_valvula_pressao = db.Column(db.Integer, nullable=False)    
    pwm_valvula_vacuo = db.Column(db.Integer, nullable=False)
    status_bomba = db.Column(db.Integer, nullable=False)
    status_pid = db.Column(db.Integer, nullable=False)
    setpoint = db.Column(db.Float, nullable=False)
    estado = db.Column(db.Integer, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Medidas {}>'.format(self.id)

class Pid(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    kp = db.Column(db.Float, nullable=False)
    kd = db.Column(db.Float, nullable=False)
    ki = db.Column(db.Float, nullable=False)
    data_registro = db.Column(db.DateTime, default=datetime.utcnow)
    def __repr__(self):
        return '<Pid {}>'.format(self.id)

class Manual(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    status_bomba = db.Column(db.Integer)
    status_pid = db.Column(db.Integer)
    pwm_valvula_pressao = db.Column(db.Integer)    
    pwm_valvula_vacuo = db.Column(db.Integer)
    def __repr__(self):
        return '<Manual {}>'.format(self.id)

class Dinamica(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    nome = db.Column(db.String(100))
    p_inicial = db.Column(db.Float)
    t_inicial = db.Column(db.Float)
    p_ref = db.Column(db.Float)
    t_atingir_ref = db.Column(db.Float)
    f_atingir_ref = db.Column(db.Float)
    t_estavel = db.Column(db.Float)
    p_ensaio = db.Column(db.Float)
    t_atingir_ensaio = db.Column(db.Float)
    f_atingir_ensaio = db.Column(db.Float)
    t_final = db.Column(db.Float)
    estado = db.Column(db.Float)
    pressao = db.Column(db.Float)
    temperatura = db.Column(db.Float)
    UR = db.Column(db.Float)
    pwm_valvula_pressao = db.Column(db.Integer)    
    pwm_valvula_vacuo = db.Column(db.Integer)
    status_bomba = db.Column(db.Integer)
    status_pid = db.Column(db.Integer)
    setpoint = db.Column(db.Float)
    def __repr__(self):
        return '<Dinamico {}>'.format(self.id)