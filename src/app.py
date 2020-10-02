from loguru import logger
from flask import Flask
from flask import jsonify, request
from core.Storage import BaseStorage
from core.Indexer import Indexer
from threading import Thread

app = Flask(__name__)
base_storage = BaseStorage()



def scan_handler(domain, max_depth, workers):
    max_depth, workers = int(max_depth), int(workers)
    indexer = Indexer(base_storage, domain, max_depth=max_depth, workers=workers)
    indexer.storage.mongo_client.drop_database('crawler')

@app.route('/scan')
def scan():
    domain = request.args.get('domain')
    max_depth = request.args.get('max_depth') or '2'
    workers = request.args.get('workers') or '5'

    Thread(target=scan_handler, args=(domain, max_depth, workers)).start()
    return jsonify({
        "status": "ok"
    })
    
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=False)    
