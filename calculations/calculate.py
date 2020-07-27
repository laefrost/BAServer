from scipy import spatial
import json
from operator import itemgetter
from normalization.norm import generate_id_list
import numpy as np
from bson.json_util import dumps


def calculate_cosine(norm_user_incident, ref_incidents, sources, events, entities, impacts, step, temp):
    print("calculate cosine ")
    cosine_list = []
    list_ref_incidents = []
    norm_ref_incidents = json.loads(ref_incidents)
    joined_user_vector = norm_user_incident["normSources"] + norm_user_incident["normEvents"] + norm_user_incident[
        "normEntities"] + norm_user_incident["normImpacts"]
    for incident in norm_ref_incidents:
        joined_ref_vector = incident["normSources"] + incident["normEvents"] + incident["normEntities"] + incident[
            "normImpacts"]
        result = 1 - spatial.distance.cosine(joined_user_vector, joined_ref_vector)
        cosine_list.append(result)
    print(cosine_list)
    for i in range(2):
        index, value = max(enumerate(cosine_list), key=itemgetter(1))
        if value == 1:
            print("found ident incident")
            return norm_ref_incidents[index]
        list_ref_incidents.append(norm_ref_incidents[index])
        cosine_list[index] = -1
        i = i + 1
    print(list_ref_incidents)
    if step == 2:
        response = create_response(get_missing_attributes_refinement(temp, list_ref_incidents, "normSources", sources),
                                   get_missing_attributes_refinement(temp, list_ref_incidents, "normEvents", events),
                                   get_missing_attributes_refinement(temp, list_ref_incidents, "normEntities", entities),
                                   get_missing_attributes_refinement(temp, list_ref_incidents, "normImpacts", impacts))
        print(response)
        return response
    elif step == 1:
        response = create_response(get_missing_attributes_completion(norm_user_incident, list_ref_incidents, "normSources", sources),
                                   get_missing_attributes_completion(norm_user_incident, list_ref_incidents, "normEvents", events),
                                   get_missing_attributes_completion(norm_user_incident, list_ref_incidents, "normEntities", entities),
                                   get_missing_attributes_completion(norm_user_incident, list_ref_incidents, "normImpacts", impacts))
        print(response)
        return response
    elif step == 3:
        return None


def create_response(s_ids, ev_ids, ent_ids, im_ids):
    response = {'sources': s_ids,
                'events': ev_ids,
                'entities': ent_ids,
                'impacts': im_ids}
    return response


def get_attribute_ids(index_list, category):
    id_list = generate_id_list(json.loads(category)[0], [])
    ids = []
    for index in index_list:
        ids.append(id_list[index])
    return ids


# get ids and create hierarchy
def get_missing_attributes_completion(incident_one, incidents, key, topic):
    print("get attributes completion")
    result = []
    for incident in incidents:
        indexes_one = np.where(np.array(incident[key]) != 0)[0]
        indexes_two = np.where(np.array(incident_one[key]) != 0)[0]
        ids_one = get_attribute_ids(indexes_one, topic)
        ids_two = get_attribute_ids(indexes_two, topic)

        for element in ids_one:
            if element not in ids_two:
                result.append(element)
    result = list(dict.fromkeys(result))
    result.sort()
    print(result)
    return result


def get_missing_attributes_refinement(incident_one, incidents, key, topic):
    result = []
    print("get missing attributes refinement")
    for incident in incidents:
        indexes_one = np.where(np.array(incident_one[key]) != 0)[0]
        indexes_two = np.where(np.array(incident[key]) != 0)[0]
        ids_one = get_attribute_ids(indexes_one, topic)
        ids_two = get_attribute_ids(indexes_two, topic)
        for element in ids_one:
            if element not in ids_two:
                result.append(element)
    result = list(dict.fromkeys(result))
    result.sort()
    print(result)
    return result


# mock function for data quality
def calculate_data_quality(step):
    if step == 1:
        print("completion")
        return 0.7
    if step == 2:
        print("refinement")
        return 0.9
