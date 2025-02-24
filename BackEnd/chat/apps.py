from django.apps import AppConfig
import mongoengine
import logging
import os
from . import models

logger = logging.getLogger(__name__)


class ChatConfig(AppConfig):
    name = "chat"

    def ready(self):
        if os.environ.get("ENSURE_INDEXES", "false").lower() == "true":
            try:
                models.Room.ensure_indexes()
                logger.info("Indexes ensured successfully.")
            except mongoengine.OperationError as e:
                logger.error(
                    f"MongoEngine operation error while ensuring indexes: {e}"
                )
                raise
            except Exception as e:
                logger.exception(
                    "Unexpected error while ensuring indexes for Room"
                )
                raise
        else:
            logger.info(
                "Skipping index creation; ENSURE_INDEXES is not set to true."
            )
