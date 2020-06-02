#!/usr/bin/python3
#coding: utf-8

from flask import render_template, request, redirect, session, flash, url_for, send_from_directory, json, jsonify
from app import app, db
from app.models import Ensaios, Medidas, Pid, Dinamica
import time

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'Ensaios': Ensaios, 'Medidas': Medidas, 'Pid': Pid, 'Dinamica': Dinamica}

if __name__ == "__main__":
    import logging
    logging.basicConfig(filename='error.log',level=logging.DEBUG)
    app.run(host='0.0.0.0',debug=True)