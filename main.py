import json
import logging.config
from pathlib import Path

with (Path(__file__).resolve().parent / "logging.conf").open("r") as f:
    logging.config.fileConfig(f)

logger = logging.getLogger(__name__)


def handler(event, context):
    if logger.isEnabledFor(logging.INFO):
        logger.info("Event: %s", json.dumps(event))

    return {
        "statusCode": 200,
        "body": "",
    }
