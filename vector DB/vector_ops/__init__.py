import logging
import os
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
LOG_FILE = os.path.join(ROOT_DIR, 'backend', 'app.log')


logging.basicConfig(
    filename = LOG_FILE,              
    level=logging.INFO,              
    format='%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
)

logger = logging.getLogger(__name__)



