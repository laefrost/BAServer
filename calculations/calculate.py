from scipy import spatial
import json
from operator import itemgetter
from normalization.norm import generate_id_list
import numpy as np


def calculate_cosine(norm_user_incident, ref_incidents, sources, events, entities, impacts, step):
    cosine_list = []
    norm_ref_incidents = json.loads(ref_incidents)
    joined_user_vector = norm_user_incident.normSources + norm_user_incident.normEvents + norm_user_incident.normEntities + norm_user_incident.normImpacts
    for incident in norm_ref_incidents:
        joined_ref_vector = incident["normSources"] + incident["normEvents"] + incident["normEntities"] + incident[
            "normImpacts"]
        result = 1 - spatial.distance.cosine(joined_user_vector, joined_ref_vector)
        cosine_list.append(result)
    index, value = max(enumerate(cosine_list), key=itemgetter(1))
    print("most Sim Incident")
    print(norm_ref_incidents[index])
    print("userIncident")
    print(norm_user_incident.to_json())
    # mock calculation of data quality
    if calculate_data_quality(step) > 0.8:
        # get ids of attributes that differ in user and reference incident
        ids = compare_lists(norm_ref_incidents[index], norm_user_incident, sources, events, entities, impacts)
    else:
        # get ids of attributes that differ in user and reference incident
        ids = compare_lists(norm_user_incident, norm_ref_incidents[index], sources, events, entities, impacts)
    return ids


def compare_lists(incident_one, incident_two, sources, events, entities, impacts):
    response = {'sources': get_question_ids(incident_two, incident_one, "normSources", sources),
                'events': get_question_ids(incident_two, incident_one, "normEvents", events),
                'entities': get_question_ids(incident_two, incident_one, "normEntities", entities),
                'impacts': get_question_ids(incident_two, incident_one, "normImpacts", impacts)}
    return response


def get_attribute_ids(indexList, category):
    id_list = generate_id_list(json.loads(category)[0], [])
    ids = []
    for index in indexList:
        ids.append(id_list[index])
    return ids


# get ids and create hierarchy
def get_question_ids(incident_one, incident_two, key, topic):
    print("getQuestionId")
    result = []
    indexes_one = np.where(np.array(incident_one[key]) != 0)[0]
    indexes_two = np.where(np.array(incident_two[key]) != 0)[0]
    ids_one = get_attribute_ids(indexes_one, topic)
    ids_two = get_attribute_ids(indexes_two, topic)
    # for element in ids_one check if in ids_two, if not then append to result, if yes then jump to next element
    for element in ids_one:
        # id = element
        while len(element) > 0:
            if element not in ids_two:
                result.append(element)
                # change value of element to create hierarchy and add parent questions to result if necessary
                element = element[:-2]
            else:
                break
    result = list(dict.fromkeys(result))
    result.sort()
    return result


# mock function for data quality
def calculate_data_quality(step):
    if step == 1:
        print("completion")
        return 0.7
    if step == 2:
        print("refinement")
        return 0.9
