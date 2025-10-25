from flask import Flask
from flask import render_template
app = Flask(__name__)
from flask import Flask, jsonify
#mi librerias
from openxlreader import read_and_print_excel_data


# Python Dictionary
data = {
    "name": "Alice",
    "age": 30,
    "city": "New York",
    "is_student": False,
    "hobbies": ["reading", "coding"]
}

@app.route("/")
def hello_world():
    return "<marquee><p>Hello, ITE!</p></marquee>"

@app.route("/jason")
def saluda():
    return data

@app.route("/json")
def saludajson():
    return jsonify(data)

@app.route("/pagina")
@app.route("/pagina/<name>")
def pagina(name=None):
    return render_template('pagina.html', person=name)

@app.route("/buscanegocio")
def buscador_negocio(id_negocio):
    #read_and_print_excel_data('datos.xlsx','6841818')
    read_and_print_excel_data(id_negocio)
