from shapely import wkt
import json
import cv2
import os

def split_list(full_list, n):
    """Split a list into n roughly equal parts."""
    if len(full_list) // n <= 10:
        return [full_list]
    k, m = divmod(len(full_list), n)
    return (full_list[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))

def get_polygon_from_image_path(image_path):
    """Read metadata from the JSON file."""

    json_path = image_path[:-3] + "json"
    
    with open(json_path) as file:
        metadata = json.load(file)

    return wkt.loads(metadata["raw_location"])

def get_image_data(image_path):
    """Read metadata from the JSON file."""
    basedir, class_name, instance_id, image_name = image_path.rsplit("/", 3)

    image = cv2.imread(image_path)
    json_path = image_path[:-3] + "json"

    with open(json_path) as file:
        metadata = json.load(file)

    object_data = []
    data = {}
    for data in metadata['bounding_boxes']:
        if "raw_category" not in data:
            continue
        box = data["box"]
        object_image = image[box[0]:box[0] + box[2], box[1]:box[1] + box[3]]


        object_data.append({
            "category": data["raw_category"],
            "box": box,
            "object_image": object_image,
            "object_polygon": wkt.loads(data["raw_location"])
        })

    data["metadata"] = metadata
    data["object_data"] = object_data
    data["full_polygon"] = wkt.loads(metadata["raw_location"])
    data["image"] = image
    data["image_path"] = os.path.join(class_name, instance_id, image_name)
    data["image_basedir"] = basedir
    return data

def get_image_paths(fmow_datapath):
    image_paths = []
    for class_folder in os.listdir(fmow_datapath):
        class_path = os.path.join(fmow_datapath, class_folder)
        if not os.path.isdir(class_path):
            continue
        for instance_folder in os.listdir(class_path):
            instance_path = os.path.join(class_path, instance_folder)
            if not os.path.isdir(instance_path):
                continue

            images = [os.path.join(instance_path, f) for f in os.listdir(instance_path) if f.endswith(('.jpg', ".png"))]
            image_paths.extend(images)

    return image_paths

def get_newest_image_paths(fmow_datapath):
    image_paths = [] 
    for class_folder in os.listdir(fmow_datapath):
        class_path = os.path.join(fmow_datapath, class_folder)
        if not os.path.isdir(class_path):
            continue
        for instance_folder in os.listdir(class_path):
            instance_path = os.path.join(class_path, instance_folder)
            if not os.path.isdir(instance_path):
                continue

            images = [f for f in os.listdir(instance_path) if f.endswith('_rgb.jpg')]
            image_path = sorted(images, key=lambda x: int(x.rsplit('_', 2)[1]))[-1]
            image_paths.append(os.path.join(instance_path, image_path))

    return image_paths
