import json
from datetime import datetime

def format_timestamp():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_data_lake_path(category, date=None):
    if not date:
        date = datetime.now()
    return f"{category}/raw/{date.strftime('%Y/%m/%d')}/"
