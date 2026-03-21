from app import create_app, db
# from app.cache import init_cache

app = create_app()
# init_cache(app) 
 
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5500, debug=True)
# docker container run -d -p 4000 or 5000(where flask listens):5500(where docker server port runs) jwt-docker --> correct
# If docker container run -d -p 5000:5000 jwt-docker --> There's a port mismatch issue: Your Flask app in run.py runs on port 5500, but your Docker command maps port 5000.


'''
Redis is a database itself (in-memory key–value store). It’s not a library or framework that you integrate into your application code. Instead, you run Redis as a separate service, and your application connects to it to perform caching operations.
🧠 How Interviewers Expect You To Explain This API

If asked:

“How did you improve API performance?”

You answer:

✅ Implemented Redis caching for paginated endpoints
✅ Cache invalidation on write operations
✅ Reduced DB reads significantly

That alone sounds 2+ years backend experience.


Automatic Cache Invalidation
💡 Interview Answer (Perfect)

If interviewer asks:

How did you handle caching?

Say:

“I implemented Redis caching using the Cache-Aside pattern (Lazy Loading Cache).
Read APIs fetch from cache first, and write operations automatically invalidate cache entries to prevent stale data.”

🔥 That sounds senior-level.
'''