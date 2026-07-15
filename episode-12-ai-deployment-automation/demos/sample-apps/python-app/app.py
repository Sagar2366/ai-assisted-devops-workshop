"""
Sample Flask Application
========================
A simple REST API with health check, Redis caching, and basic CRUD.
Used as input for the AI deployment automation pipeline.
"""

import os
from flask import Flask, jsonify, request
from redis import Redis

app = Flask(__name__)

# Configuration
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
redis_client = Redis.from_url(REDIS_URL, decode_responses=True)


@app.route("/health")
def health():
    """Health check endpoint for container orchestrators."""
    try:
        redis_client.ping()
        return jsonify({"status": "healthy", "redis": "connected"}), 200
    except Exception:
        return jsonify({"status": "degraded", "redis": "disconnected"}), 200


@app.route("/")
def index():
    """Root endpoint."""
    return jsonify({
        "service": "python-flask-app",
        "version": "1.0.0",
        "endpoints": ["/", "/health", "/items", "/items/<id>"]
    })


@app.route("/items", methods=["GET"])
def list_items():
    """List all items from the cache."""
    keys = redis_client.keys("item:*")
    items = []
    for key in keys:
        item = redis_client.hgetall(key)
        item["id"] = key.split(":")[1]
        items.append(item)
    return jsonify({"items": items, "count": len(items)})


@app.route("/items", methods=["POST"])
def create_item():
    """Create a new item."""
    data = request.get_json()
    if not data or "name" not in data:
        return jsonify({"error": "name is required"}), 400

    item_id = redis_client.incr("item_counter")
    key = f"item:{item_id}"
    redis_client.hset(key, mapping={
        "name": data["name"],
        "description": data.get("description", ""),
    })

    return jsonify({"id": item_id, "name": data["name"]}), 201


@app.route("/items/<int:item_id>", methods=["GET"])
def get_item(item_id):
    """Get a single item by ID."""
    key = f"item:{item_id}"
    item = redis_client.hgetall(key)
    if not item:
        return jsonify({"error": "item not found"}), 404
    item["id"] = item_id
    return jsonify(item)


@app.route("/items/<int:item_id>", methods=["DELETE"])
def delete_item(item_id):
    """Delete an item by ID."""
    key = f"item:{item_id}"
    if not redis_client.exists(key):
        return jsonify({"error": "item not found"}), 404
    redis_client.delete(key)
    return jsonify({"deleted": item_id}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV") == "development"
    app.run(host="0.0.0.0", port=port, debug=debug)
