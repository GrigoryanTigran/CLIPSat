import sys
import os
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from generation.osm_data_processing import extract_OSM_data
from generation.utils import get_image_data
from flask import Flask, render_template, request, jsonify
import pandas as pd
import shutil

import os

app = Flask(__name__)
current_file_paths = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    if file:
        filepath = os.path.join('static/uploads', file.filename)
        file.save(filepath)
        return jsonify({'success': 'File uploaded', 'filepath': filepath})

@app.route('/submit', methods=['POST'])
def submit():
    global current_file_paths
    filepath = request.json['filepath']
    print(filepath, "AAAA")
    try:
        df = pd.read_csv(filepath, sep=";")
        current_file_paths = df['FilePath']
        print("ASA", current_file_paths)
        df["Base Category"] = df['FilePath'].apply(lambda data: data.rsplit("/", 1)[1].rsplit("_", 5)[0].replace("_", " "))
        df["GSD"] = df["GSD"].apply(lambda data: round(data, 3))
        df = df[["Base Category", "Text", "GSD"]]
        # Convert the DataFrame to HTML table; basic, you can customize it further
        html_table = df.to_html(classes='data', index=False, border=0, justify='left')
        return jsonify({'html_table': html_table})
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/process-row', methods=['POST'])
def process_row():
    row_id = request.json.get('rowId')
    print(f"Processing row ID: {row_id}")
    # Add your logic here, e.g., process data related to this row ID
    image_path = current_file_paths[row_id]
    image_path = "../generation/" + image_path
    image_data = get_image_data(image_path)
    osm_path = image_path[:-3] + "csv"
    osm_data = pd.read_csv(osm_path, sep=";")
    extracted_osm_data = extract_OSM_data(osm_data)
    print(extracted_osm_data)
    dst = os.path.join('static', 'uploads', 'images', os.path.basename(image_path))
    shutil.copyfile(image_path, dst)

    return jsonify({"rowId": row_id, 
                    "image_polygon": image_data["full_polygon"].wkt,
                    "image_path": dst,
                    })

if __name__ == '__main__':
    app.run(debug=True)
