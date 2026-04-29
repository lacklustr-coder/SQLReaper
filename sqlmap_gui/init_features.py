"""
Initialize all new features and modules
"""

import logging

from api_routes import register_extended_routes
from database import init_database
from payloads import init_default_payloads
from queue_processor import queue_processor
from templates import init_default_templates
from websocket_manager import init_socketio

logger = logging.getLogger(__name__)


def initialize_all_features(app):
    """Initialize all new features"""
    from auth import register_auth_routes

    logger.info("Initializing database...")
    init_database()

    logger.info("Initializing default payloads...")
    try:
        init_default_payloads()
    except Exception as e:
        logger.warning(f"Payload initialization: {e}")

    logger.info("Initializing scan templates...")
    try:
        init_default_templates()
    except Exception as e:
        logger.warning(f"Template initialization: {e}")

    logger.info("Initializing WebSocket support...")
    socketio = init_socketio(app)

    logger.info("Starting scan queue processor...")
    queue_processor.start()

    logger.info("Registering authentication routes...")
    register_auth_routes(app)

    logger.info("Registering extended API routes...")
    register_extended_routes(app)

    logger.info("All features initialized successfully")

    return socketio
