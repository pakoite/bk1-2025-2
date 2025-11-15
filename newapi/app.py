# app.py
from flask import Flask, jsonify, request
from excel_source import excel_bp
from sqlite_source import sqlite_bp
from mysql_source import mysql_bp

app = Flask(__name__)

app.register_blueprint(excel_bp, url_prefix='/api/excel')
app.register_blueprint(sqlite_bp, url_prefix='/api/sqlite')
app.register_blueprint(mysql_bp, url_prefix='/api/mysql')

if __name__ == '__main__':
    app.run(debug=True)
