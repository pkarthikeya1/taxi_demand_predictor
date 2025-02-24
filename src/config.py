from logging import raiseExceptions
import os
from dotenv import load_dotenv

from src.paths import PARENT_DIR


# load key-value pairs from .env file located in the parent dorectory

load_dotenv(PARENT_DIR/'.env')

HOPSWORKS_PROJECT_NAME = 'karthikeyap'
try:
    HOPSWORKS_API_KEY = os.environ["HOPSWORKS_API_KEY"]
except:
    raise Exception("Create an .env file on the project with the HOPSWORKS_API_KEY")

FEATRURE_GROUP_NAME = "time_series_hourly_feature_group"
FEATRURE_GROUP_VERSION = 1
FEATURE_VIEW_NAME = 'time_series_hourly_feature_view'
FEATURE_VIEW_VERSION = 1

N_FEATURES = 24 * 28

MODEL_NAME = 'taxi_demad_predictor_next_hour'
MODEL_VERSION = 3