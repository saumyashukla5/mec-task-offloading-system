from flask import Flask, request, jsonify
import time
import os

app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "server": "MEC_Edge_Host"})

@app.route('/process', methods=['POST'])
def process():
    data = request.get_json(silent=True) or {}
    task_type    = data.get('task_type', 'unknown')
    payload_size = data.get('payload_size', 0)
    task_id      = data.get('task_id', 'N/A')

  
    time.sleep(0.0005)

    return jsonify({
        "status":          "success",
        "server":          "MEC_Edge_Host",
        "task_id":         task_id,
        "task_type":       task_type,
        "payload_size_kb": payload_size,
        "processing_ms":   10
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    print(f"[EDGE SERVER] Starting on port {port}")
    app.run(host='0.0.0.0', port=port)
