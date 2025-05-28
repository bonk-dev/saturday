import logging
from flask import Flask
from flask_restx import Api
from dotenv import load_dotenv

from backend.routes.inserts.gscholar import ns_gscholar
from backend.routes.inserts.scopusApi import ns_scopus_api
from backend.routes.inserts.scopusBatch import ns_scopus_batch
from backend.routes.inserts.system import ns_system
from backend.routes.queries.dynamicChart import ns_dynamicChart
from backend.routes.queries.filterOptions import ns_filter_options
from database.dbContext import init_app
from backend.config import config
from flask_cors import CORS
# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
# Configure Flask-RESTX for Swagger
api = Api(app,
          version='1.0',
          title='Science Publication Metadata Scraper API',
          description='API for scraping publication metadata from Google Scholar, Scopus API, and Scopus Batch Export',
          doc='/swagger/'
          )

# Configure logging
logging.basicConfig(level=getattr(logging, config.log_level.upper()))
logger = logging.getLogger(__name__)


api.add_namespace(ns_gscholar)
api.add_namespace(ns_scopus_api)
api.add_namespace(ns_scopus_batch)
api.add_namespace(ns_system)
api.add_namespace(ns_dynamicChart)
api.add_namespace(ns_filter_options)



init_app(app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)