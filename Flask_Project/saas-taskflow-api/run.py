from app import create_app, db
# from app.cache import init_cache

app = create_app()
# init_cache(app) 
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5500, debug=True)