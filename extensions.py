from slowapi import Limiter
from slowapi.util import get_remote_address
import structlog
import logging

# Rate Limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["10/minute"])

# Audit Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[logging.FileHandler("audit.log"), logging.StreamHandler()]
)
structlog.configure(
    processors=[structlog.processors.JSONRenderer()],
    logger_factory=structlog.stdlib.LoggerFactory(),
)
audit_logger = structlog.get_logger("audit") 