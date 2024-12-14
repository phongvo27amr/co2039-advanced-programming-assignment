from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import os

app = Flask(__name__)

# Global DataFrame to store preloaded CSV data
data_df = None

# Load CSV data into a pandas DataFrame during app startup
def preload_csv(file_path):
  global data_df
  try:
    data_df = pd.read_csv(file_path, encoding='utf-8-sig')
    print(f"Data loaded: {len(data_df)} rows")
    return list(data_df.columns)
  except Exception as e:
    print(f"Error loading CSV: {e}")
    return []

# Filter data using pandas
def filter_data(conditions):
  global data_df

  if data_df is None:
    return []

  filtered_df = data_df.copy()

  for column, value in conditions.items():
    if column == 'credit':
      if isinstance(value, tuple): # Range query
        min_value, max_value = value
        filtered_df = filtered_df[(filtered_df['credit'] >= min_value) & (filtered_df['credit'] <= max_value)]
      else: # Single value
        filtered_df = filtered_df[filtered_df['credit'] == value]
    elif column == 'date_time':
      filtered_df = filtered_df[filtered_df['date_time'].str.contains(value, na=False)]
    elif column == 'trans_no':
      try:
        value = int(value) # Ensure the input is numeric
        filtered_df = filtered_df[filtered_df['trans_no'] == value]
      except ValueError:
        # If value is not a valid number, skip filtering this column
        continue
    else:
      filtered_df = filtered_df[filtered_df[column].str.contains(value, na=False, case=False)]

  return filtered_df.to_dict(orient='records')

# Endpoint to serve the index.html file
@app.route('/')
def serve_index():
  return send_from_directory(os.path.dirname(os.path.abspath(__file__)), 'index.html')

# Endpoint to get CSV column names
@app.route('/columns', methods=['GET'])
def get_columns():
  global data_df
  if data_df is None:
    return jsonify({"error": "Data not loaded"}), 500
  return jsonify({"columns": list(data_df.columns)})

# Endpoint to search CSV data
@app.route('/query', methods=['GET'])
def search():
  global data_df

  if data_df is None:
    return jsonify({"error": "Data not loaded"}), 500

  search_conditions = {}

  for key, value in request.args.items():
    if key.lower() == 'q': # Query for detail
      search_conditions['detail'] = value
    elif key.lower() == 'credit':
      try:
        if '-' in value:
          min_value, max_value = map(float, value.split('-'))
          if min_value > max_value:
            return jsonify({"error": "Invalid range: min_value cannot be greater than max_value"}), 400
          search_conditions[key] = (min_value, max_value)
        else:
          search_conditions[key] = float(value) # Single value
      except ValueError:
          return jsonify({"error": "Invalid credit value"}), 400
    elif key.lower() == 'date_time':
        if not pd.Series([value]).str.match(r'\d{2}/\d{2}/\d{4}').bool():
            return jsonify({"error": "Invalid date_time format. Use DD/MM/YYYY."}), 400
        search_conditions[key] = value
    else:
        search_conditions[key] = value

  results = filter_data(search_conditions)

  return jsonify({"results": results, "count": len(results)})

if __name__ == '__main__':
  file_path = 'chuyen_khoan.csv'
  preload_csv(file_path)
  app.run(debug=True, host='0.0.0.0', port=5000)
