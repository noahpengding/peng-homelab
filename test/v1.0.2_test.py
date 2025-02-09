import os
import sys
import time

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from app.services.upgrader.upgrade_handler import upgrade_handler

upgrade_handler("minio", "minio")
