from flask import Flask, request, jsonify, send_from_directory
import csv
import os

app = Flask(__name__)

# Function to read columns from the CSV file
def read_columns(file_path):
  try:
    with open(file_path, mode='r', newline='') as file:
      reader = csv.DictReader(file)
      columns = reader.fieldnames
      return columns
  except Exception as e:
    return str(e)

# Endpoint to serve the index.html file
@app.route('/')
def serve_index():
  return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

# Endpoint to get CSV column names
@app.route('/columns', methods=['GET'])
def get_columns():
  file_path = 'chuyen_khoan.csv'
  columns = read_columns(file_path)
  if isinstance(columns, str):
    return jsonify({"error": columns}), 500
  return jsonify({"columns": columns})

# Endpoint to search CSV data
@app.route('/query', methods=['GET'])
def search():
  file_path = 'chuyen_khoan.csv'
  search_conditions = {}

  for key, value in request.args.items():
    if key == 'credit_min' or key == 'credit_max':
      search_conditions[key] = float(value)
    else:
      search_conditions[key] = value.lower()

  if not search_conditions:
    return jsonify({"error": "No search conditions provided"}), 400

  results = search_csv(file_path, search_conditions)
  if isinstance(results, str):
    return jsonify({"error": results}), 500

  return jsonify({"results": results})

def search_csv(file_path, search_conditions):
  try:
    with open(file_path, mode='r', newline='') as file:
      reader = csv.DictReader(file)
      results = []

      for row in reader:
        match = True
        for column_name, search_term in search_conditions.items():
          if column_name == 'credit_min':
            if float(row['credit']) < search_term:
              match = False
              break
          elif column_name == 'credit_max':
            if float(row['credit']) > search_term:
              match = False
              break
          else:
            if search_term not in row[column_name].lower():
              match = False
              break
        if match:
          results.append(row)

      return results
  except Exception as e:
    return str(e)

if __name__ == '__main__':
  app.run(debug=True)