from flask import Flask, request, jsonify
import csv, io, os

app = Flask(__name__)

# Tool registry (simple discovery)
@app.get('/mcp/tools')
def list_tools():
    return jsonify({
        'tools': [
            {'name':'file_read_csv','description':'Read CSV from local disk and return preview + columns'},
            {'name':'compute_stats','description':'Compute count/sum/mean for a numeric column'}
        ]
    })

@app.post('/mcp/tools/file_read_csv')
def file_read_csv():
    data = request.get_json(force=True)
    file_path = data.get('filePath','/opt/data/orders_4000_lines.csv')
    sample = int(data.get('sample',10))
    if not os.path.exists(file_path):
        return jsonify({'error': f'File not found: {file_path}'}), 400
    with open(file_path,'r',encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)
    preview = rows[:sample]
    columns = list(preview[0].keys()) if preview else []
    return jsonify({'columns': columns, 'previewCount': len(preview), 'preview': preview})

@app.post('/mcp/tools/compute_stats')
def compute_stats():
    data = request.get_json(force=True)
    rows = data.get('rows',[])
    column = data.get('column')
    if not column:
        return jsonify({'error':'column is required'}), 400
    vals = []
    for r in rows:
        try:
            v = float(r.get(column, 'nan'))
            if v == v:  # not NaN
                vals.append(v)
        except Exception:
            pass
    count = len(vals)
    s = sum(vals)
    mean = s / count if count else 0.0
    return jsonify({'column': column, 'count': count, 'sum': s, 'mean': mean})

if __name__ == '__main__':
    port = int(os.environ.get('PORT','8080'))
    app.run(host='0.0.0.0', port=port)