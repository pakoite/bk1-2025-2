# excel_source.py
from flask import Blueprint, jsonify
import pandas as pd

excel_bp = Blueprint('excel', __name__)

@excel_bp.route('/', methods=['GET'])
def get_all():
    df = pd.read_excel('data.xlsx')
    return jsonify(df.to_dict(orient='records'))

@excel_bp.route('/<int:id>', methods=['GET'])
def get_by_id(id):
    df = pd.read_excel('data.xlsx')
    record = df[df['id'] == id]
    if record.empty:
        return jsonify({'error': 'Not found'}), 404
    return jsonify(record.to_dict(orient='records')[0])
