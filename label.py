import json
import re
from flipside import Flipside
import pandas as pd


# Recursively iterate over the json object looking for specified pattern
def explore_json(obj, items, pattern):
    try:
        if isinstance(obj, dict):
            for value in obj.values():
                if isinstance(value, str) and re.match(pattern, value):
                    items.append(value)
                explore_json(value, items, pattern)
        elif isinstance(obj, list):
            for item in obj:
                explore_json(item, items, pattern)
        else:
            pass
    
    except Exception as e:
        print("explore_json error: ", e)


# Extract the unique occurences of the specified pattern
def extract(json_obj, pattern = None):
    try:
        items = []
        explore_json(json_obj, items, pattern)
        unique_items = list(set(items))
        return unique_items
    
    except Exception as e:
        print("extract error: ", e)


# Make the addresses into a string that will be used in the flipside query
def format (addresses):
    addresses_str = ', '.join([f"'{address}'" for address in addresses if address])
    return addresses_str


# Query Flipside
def query_flipside (addresses_str, endpoint):
    sql = f"""
        select address,
            address_name,
            label,
            label_type,
            label_subtype
        from ethereum.core.dim_labels 
        where lower(address) in ({addresses_str})
        """

    query_result_set = endpoint.query(sql)
    df = pd.DataFrame(query_result_set)
    return df

# Put results into a json object
def to_json(df):
    try:
        json_data = []
        data = df[1][4]
        if data is None:
            print("Data is None, returning an empty JSON object")
            return json.dumps({'address_labels': []}, indent=4)

        for index, item in enumerate(data):
            json_data.append({
                'address': item[0],
                'address_name': item[1],
                'label': item[2],
                'label_type': item[3],
                'label_subtype': item[4]
            })
    
        json_object = json.dumps({'address_labels': json_data}, indent=4)
        return json_object
    except Exception as e:
        print("Error at to_json: ", e)

# Fetch address labels
def fetch_address_labels(sim_data, endpoint):
    address_regex = r'^0x[0-9a-fA-F]{40}$'
    try:
        addresses = extract(sim_data, address_regex)
        addresses_str = format(addresses)
        labels_data = query_flipside(addresses_str,endpoint)
        labels_json = to_json(labels_data)
        return labels_json
    except Exception as e:
        print("Error at fetch_address_labels: ", e)

# Add address labels to the original sim_data
def add_labels(sim_data, endpoint):
    try:
        labels_json = json.loads(fetch_address_labels(sim_data, endpoint))
        for key, value in labels_json.items():
            sim_data[key] = value
        
        return sim_data
    except Exception as e:
        print("Error at add_labels: ", e)

