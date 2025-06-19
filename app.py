import os
from flask import Flask, request, jsonify # type: ignore
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def careerjet_search(keywords, location, page_number=1, pagesize=100):
    url = 'http://public.api.careerjet.net/search'

    params = {
        'keywords': keywords,
        'location': location,
        'page': page_number,
        'pagesize': pagesize,
        'affid': '7db47854c2e9ab12057974e94f96bfca',  # your affiliate ID
        'user_ip': '1.2.3.4',
        'user_agent': 'Mozilla/5.0',
        'locale_code': 'en_US',
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data.get('type') == 'JOBS':
        return data['jobs']
    else:
        return []

@app.route('/search_jobs', methods=['GET'])
def search_jobs():
    keywords = request.args.get('keywords', '')
    location = request.args.get('location', '')
    page = int(request.args.get('page', 1))
    pagesize = int(request.args.get('pagesize', 10))

    jobs = careerjet_search(keywords, location, page, pagesize)
    return jsonify({'success': True, 'jobs': jobs})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)