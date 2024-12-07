import csv
import os
from flask import Flask, request, jsonify, send_from_directory
from datetime import datetime

app = Flask(__name__)

# Function to read columns from the CSV file
def read_columns(file_path):
  try:
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
      reader = csv.DictReader(file)
      columns = reader.fieldnames  # Get column names from the CSV header
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
  file_path = 'chuyen_khoan.csv'  # Fixed file name
  search_conditions = {}

  for key, value in request.args.items():
    if key.lower() == 'credit':  # Handle credit column differently
      if '-' in value:
        try:
          min_value, max_value = map(float, value.split('-'))
          if min_value > max_value:  # Validate range logic
            return jsonify({"error": f"Invalid range for {key}. Min value must be less than or equal to max value."}), 400
          search_conditions[key] = (min_value, max_value)
        except ValueError:
          return jsonify({"error": f"Invalid range format for {key}. Use min-max format, e.g., 10000-20000."}), 400
      else:
        try:
          min_value = float(value)
          search_conditions[key] = (min_value, min_value)  # Treat single value as exact match
        except ValueError:
          return jsonify({"error": f"Invalid number format for {key}. Ensure it is a numeric value."}), 400

    # Validate date_time format
    elif key.lower() == 'date_time':
      try:
        datetime.strptime(value, '%d/%m/%Y')  # Check if the date is in DD/MM/YYYY
        search_conditions[key] = value
      except ValueError:
        return jsonify({"error": f"Invalid date format for {key}. Use DD/MM/YYYY format."}), 400
    else:
      search_conditions[key] = value

  if not search_conditions:
    return jsonify({"error": "No search conditions provided"}), 400

  results = search_csv(file_path, search_conditions)
  if isinstance(results, str):  # Error handling
    return jsonify({"error": results}), 500

  return jsonify({"results": results})

def search_csv(file_path, search_conditions):
  try:
    with open(file_path, mode='r', newline='', encoding='utf-8-sig') as file:
      reader = csv.DictReader(file)
      results = []

      for row in reader:
        match = True
        for column_name, search_term in search_conditions.items():
          if column_name in row:
            if column_name.lower() == 'credit':
              min_value, max_value = search_term
              credit_value = float(row[column_name])
              if not (min_value <= credit_value <= max_value):
                match = False
                break
            else:
              if search_term.lower() not in row[column_name].lower():
                match = False
                break
        if match:
          results.append(row)

      return results
  except Exception as e:
    return str(e)

if __name__ == '__main__':
  app.run(debug=True)
