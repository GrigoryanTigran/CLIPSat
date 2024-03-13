import pandas as pd
from shapely import wkt

def extract_OSM_data(features):
    full_data = {}
    #print("Data firstly contains", features.shape[0], "inforamtion.")
    aeroway, features = get_data(features, 'aeroway', process_aeroway)
    full_data.update(aeroway)
    #print("After filtering aeroways remains", features.shape[0], "information.")
    natural, features = get_data(features, 'natural', process_natural)
    full_data.update(natural)
    #print("After filtering naturals remains", features.shape[0], "information.")
    man_made, features = get_data(features, 'man_made', process_man_made)
    full_data.update(man_made)
    #print("After filtering man_made remains", features.shape[0], "information.")
    railway, features = get_data(features, 'railway', process_railway)
    full_data.update(railway)
    #print("After filtering railways remains", features.shape[0], "information.")
    waterway, features = get_data(features, 'waterway', process_waterway)
    full_data.update(waterway)
    #print("After filtering waterway remains", features.shape[0], "information.")
    highway, features = get_data(features, 'highway', process_highway)
    full_data.update(highway)
    #print("After filtering highway remains", features.shape[0], "information.")
    building, features = get_data(features, 'building', process_building)
    full_data.update(building)
    #print("After filtering building remains", features.shape[0], "information.")
    amenity, features = get_data(features, 'amenity', process_amenity)
    full_data.update(amenity)
    #print("After filtering amenity remains", features.shape[0], "information.")
    landuse, features = get_data(features, 'landuse', process_landuse)
    full_data.update(landuse)
    #print("After filtering all remains", features.shape[0], "information.")

    return full_data

def give_id(data, col):
    data['ID'] = (data.groupby(col).cumcount() + 1)
    data["ID"] = data["ID"].fillna(0)
    data["ID"] = data["ID"].astype(int).astype(str)

    # Update 'A' to include this ID, making each value unique
    data[col] = data[col] + '-' + data['ID']

    # Drop the 'ID' column as it's no longer needed
    data.drop(columns=['ID'], inplace=True)
    return data

def add_type(data, col):
    for index, row in data.iterrows():
        type_col = f"{row[col]}:type"  # Construct the column name
        if type_col in data.columns and pd.notna(row[type_col]):
            # Update 'col' if corresponding ':type' column exists and has a non-NaN value
            data.at[index, col] = f"{row[type_col]} {row[col]}"
    return data

def get_data(features, col, process_data):
    if col not in features:
        return {}, features
    
    data = features[features[col].notnull()]
    data = data.dropna(axis='columns', how='all')
    if not len(data):
        return {}, features
    data = data.replace("_", " ")
    data = process_data(data)
    data = give_id(data, col)
    data['geometry'] = data['geometry'].apply(wkt.loads)
    data = data.set_index(col)["geometry"].to_dict()
    features = features[features[col].isnull()]
    return data, features

def process_aeroway(data):
    #data = data.fullna("")
    data = add_type(data, "aeroway")
    data['aeroway'] = data['aeroway'] + " in aeroway"
    return data

def process_natural(data):
    data = add_type(data, "natural")
    data['natural'] = "natural " + data['natural']
    return data

def process_man_made(data):
    data = add_type(data, "man_made")
    data['man_made'] = "man made " + data['man_made']
    return data

def process_railway(data):
    data = add_type(data, "railway")
    data = data.fillna("")
    data['railway'] = data.get("usage", "") + " " + data.get("service", "") + " " + data['railway'] + ' railway'
    data['railway'] = data['railway'].str.replace(r'\s+', ' ', regex=True).str.strip()
    return data

def process_waterway(data):
    data = add_type(data, "waterway")
    if "tunnel" in data.columns:
        data['tunnel'] = " with " + data['tunnel'] + " tunnel"
    data = data.fillna("")
    data['waterway'] += " waterway" + data.get('tunnel', "")
    return data

def process_highway(data):
    data = add_type(data, "highway")
    for col in ["oneway", "bridge", "junction", "surface"]:
        if col not in data.columns:
            data.loc[:, col] = pd.Series([""] * len(data), name=col)
    data = data.fillna("")

    data.loc[data["oneway"] == "yes", "oneway"] = "oneway "
    data.loc[data["oneway"] == "no", "oneway"] = "twoway "
    data.loc[data["bridge"] == "yes", "bridge"] = "bridge "
    data.loc[data["junction"] != "", "junction"] = data.loc[data["junction"] != "", "junction"] + " junction "
    data["highway"] = data["oneway"] + data["surface"] + " " + data["highway"] + " " + data["bridge"] + data["junction"] + " highway"
    data['highway'] = data['highway'].str.replace(r'\s+', ' ', regex=True).str.strip()

    return data

def process_building(data):
    data.loc[data["building"] == "yes", "building"] = ""
    data = add_type(data, "building")
    data = data.fillna("")
    data['building'] = data.get('office', "") + data.get('tourism', "") + " " + data.get('amenity', "") + " " + \
                        data.get("roof:material", "") + " " + data.get('roof:shape', "") + " " + data.get('building', "") + " building"
    data['building'] = data['building'].str.replace(r'\s+', ' ', regex=True).str.strip()
    return data

def process_amenity(data):
    data = data.fillna('')
    data['amenity'] = data.get('landuse', "") + " " + data.get('amenity', "") + " amenity"
    data['amenity'] = data.get('amenity', "").str.replace(r'\s+', ' ', regex=True).str.strip()
    return data

def process_landuse(data):
    data = data.fillna('')
    data['landuse'] = data.get('barrier', "") + " " + data.get("sport", "") + " " + data.get('leisure', "") + " " + data.get('landuse', "") + " landuse"
    data['landuse'] = data.get('landuse', "").str.replace(r'\s+', ' ', regex=True).str.strip()

    return data
