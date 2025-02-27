import sys
import os

# # Add the parent directory to the Python path
# script_dir = os.getcwd() # Get the current working directory
# sys.path.append(os.path.abspath(os.path.join(script_dir, '..')))

from datetime import datetime, timedelta
import pandas as pd
import hopsworks

import src.config as config
from src.data import load_raw_data
from src.data import transform_raw_data_into_ts_data

current_date= pd.Timestamp("2024-03-01").floor('h')
print(f"{current_date=}")


# we fetch raw data for the last 28 days, to add redundancy to our pipeline
fetch_data_to=current_date
fetch_data_from = current_date - timedelta(days=28)




def fetch_batch_raw_data(from_date: datetime, to_date: datetime) -> pd.DataFrame:
    """
    Simulate production data by sampling historical data from 52 weeks ago (i.e., 1 year)
    """
    from_date_ = from_date - timedelta(days=7*52)
    to_date_ = to_date - timedelta(days=7*52)
    print(f'{from_date=}, {to_date_=}')

    # download 2 files from website
    rides = load_raw_data(year=from_date_.year, months=from_date_.month)
    rides = rides[rides.pickup_datetime >= from_date_]
    rides_2 = load_raw_data(year=to_date_.year, months=to_date_.month)
    rides_2 = rides_2[rides_2.pickup_datetime < to_date_]

    rides = pd.concat([rides, rides_2])

    # shift the data to pretend this is recent data
    rides['pickup_datetime'] += timedelta(days=7*52)

    rides.sort_values(by=['pickup_location_id', 'pickup_datetime'], inplace=True)

    return rides

rides = fetch_batch_raw_data(from_date= fetch_data_from, to_date= fetch_data_to)

ts_data = transform_raw_data_into_ts_data(rides)
# string to datetime
ts_data['pickup_hour'] = pd.to_datetime(ts_data['pickup_hour'], utc=True)
ts_data['pickup_location_id']=ts_data['pickup_location_id'].astype('Int64')
# add column with Unix epoch milliseconds
# ts_data['pickup_hour'] = ts_data['pickup_hour'].astype('int64').astype('int64') // 10**6



# connect to the project
project = hopsworks.login(
    project=config.HOPSWORKS_PROJECT_NAME,
    api_key_value= config.HOPSWORKS_API_KEY
)

# connect to the feature store

feature_store = project.get_feature_store()


# connect to the feature group

feature_group = feature_store.get_or_create_feature_group(
                name= config.FEATRURE_GROUP_NAME,
                version = config.FEATRURE_GROUP_VERSION,
                description = 'Time-series data at hourly frequency',
                primary_key = ["pickup_location_id","pickup_hour"],
                event_time = "pickup_hour"
                )


feature_group.insert(ts_data, write_options={"wait_for_job": False})