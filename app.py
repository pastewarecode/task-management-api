# app.py
from flask import Flask, request, jsonify, abort
from datetime import datetime

app = Flask(__name__)

# In-memory tasks store
tasks = []
next_id = 1

def get_next_id():
    global next_id
    nid = next_id
    next_id += 1
    return nid

@app.route("/tasks", methods=["POST"])
def create_task():
    data = request.get_json(force=True, silent=True)
    if not data or "title" not in data:
        return jsonify({"error": "Missing 'title' in JSON body"}), 400

    task = {
        "id": get_next_id(),
        "title": data.get("title"),
        "completed": bool(data.get("completed", False)),
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    tasks.append(task)
    return jsonify(task), 201

@app.route("/tasks", methods=["GET"])
def get_tasks():
    return jsonify(tasks), 200

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    for i, t in enumerate(tasks):
        if t["id"] == task_id:
            deleted = tasks.pop(i)
            return jsonify({"deleted": deleted}), 200
    return jsonify({"error": "Task not found"}), 404

if __name__ == "__main__":
    # For local debug; container will run via gunicorn if desired
    app.run(host="0.0.0.0", port=5000, debug=True)