from app import app

if _name_ == "_main_":
    app.run(host="0.0.0.0", port=5000, debug=True)
