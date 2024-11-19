from src.app import app
from src.util import logger


if __name__ == "__main__":
    logger.info("Development server started")
    app.run(port=30000, debug=True, load_dotenv=False)
