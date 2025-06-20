import os, logging
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)
logging.basicConfig(level=logging.INFO)

CAREERJET_AFFID = os.getenv("CAREERJET_AFFID", "7db47854c2e9ab12057974e94f96bfca")
CAREERJET_URL   = "http://public.api.careerjet.net/search"   # keep http here – API is http‑only

def careerjet_search(keywords, location, page=1, pagesize=10):
    params = {
        "keywords": keywords,
        "location": location,
        "page": page,
        "pagesize": pagesize,
        "affid": CAREERJET_AFFID,
        "user_ip": request.remote_addr or "0.0.0.0",
        "user_agent": request.headers.get("User-Agent", "Mozilla/5.0"),
        "locale_code": "en_US",
        "url": request.base_url                     # ← mandatory and unique
    }
    try:
        r = requests.get(CAREERJET_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()                             # will fail cleanly if not JSON
        return data["jobs"] if data.get("type") == "JOBS" else []
    except (requests.RequestException, ValueError) as err:
        app.logger.error("Careerjet error: %s", err)
        raise                                          # propagate → 500 so client knows

@app.route("/search_jobs")
def search_jobs():
    try:
        jobs = careerjet_search(
            keywords=request.args.get("keywords", ""),
            location=request.args.get("location", ""),
            page=int(request.args.get("page", 1)),
            pagesize=int(request.args.get("pagesize", 10)),
        )
        return jsonify(success=True, jobs=jobs)
    except Exception as e:
        return jsonify(success=False, error=str(e)), 500


# Gunicorn will import app:app, so only run the dev server locally
@app.route('/')
def home():
    return 'Job Search API is running'
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
