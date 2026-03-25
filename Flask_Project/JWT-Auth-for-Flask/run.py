from main import create_app, db

app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5500, debug=True)
# docker container run -d -p 4000 or 5000(where flask listens):5500(where docker server port runs) jwt-docker --> correct
# If docker container run -d -p 5000:5000 jwt-docker --> There's a port mismatch issue: Your Flask app in run.py runs on port 5500, but your Docker command maps port 5000.
