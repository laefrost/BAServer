import json
import numpy as np
from database.models.incident import Incident
from database.models.normIncident import NormIncident
from database.models.normUserIncidents import NormUserIncident
from database.models.userIncident import UserIncident


# generates list of attribute ids
def generate_id_list(elements, result):
    for element in elements['elements']:
        t = 'elements'
        if t in element:
            id = element.get("id")
            result.append(id)
            generate_id_list(element, result)
        else:
            result.append(element.get("id"))
    return result


# generates list of attribute names
def generate_name_list(elements, result):
    for element in elements['elements']:
        t = 'elements'
        if t in element:
            name = element.get("name")
            result.append(name)
            generate_name_list(element, result)
        else:
            result.append(element.get("name"))
    print(result)
    return result


# generates list/vector consisting of 0 and 1
def generate_vector_list(list, incident, topic, topic_singular):
    vector = {}
    for i in range(len(list)):
        if incident[topic] is not None and len(incident[topic]) > 0:
            for element in incident[topic]:
                element_list = element[topic_singular]
                if len(element_list) != 0:
                    id = element_list[-1]
                    if id == list[i]:
                        vector[i] = 1
                    else:
                        if vector.get(i) != 1:
                            vector[i] = 0
                else:
                    vector[i] = 0
        else:
            vector[i] = 0
    result = [*vector.values()]
    return result


# toDo: redo, not finished yet
def reverse_norm_incident(norm_incident, sources, events, entities, impacts, ):
    # get index where is 1 get id, add id at end of incident
    # move foreward in id and add attributenames for id at incident
    sourcesNI = np.array(norm_incident['sources'])
    eventsNI = np.array(norm_incident['events'])
    entitiesNI = np.array(norm_incident['entities'])
    impactsNI = np.array(norm_incident['impacts'])
    indexNi = np.where(sourcesNI != 0)[0]
    sourcesIds = generate_id_list(json.loads(sources)[0], [])
    sourcesIdArray = np.array(sourcesIds)
    sourcesNames = generate_name_list(json.loads(sources)[0], [])
    sources = []
    for index in indexNi:
        # create source obj at incident
        source = []
        # add id of index at end
        id = sourcesIds[index]
        source.append(id)
        source.insert(0, sourcesNames[index])
        # go through id and add name at the front
        while id[:-2]:
            indexnew = np.where(sourcesIdArray == id[:-2])
            source.insert(0, sourcesNames[indexnew])
        sources.append(source)


# generates normalized incident
def normalize_incident(incident, sources, events, entities, impacts):
    list_source = generate_id_list(json.loads(sources)[0], [])
    list_events = generate_id_list(json.loads(events)[0], [])
    list_entities = generate_id_list(json.loads(entities)[0], [])
    list_impacts = generate_id_list(json.loads(impacts)[0], [])
    if type(incident) is Incident:
        norm = NormIncident()
    elif type(incident) is UserIncident:
        norm = NormUserIncident()

    norm.title = incident["title"]
    norm.refId = incident["myId"]
    norm.normSources = generate_vector_list(list_source, incident, 'sources', 'source')
    norm.normEvents = generate_vector_list(list_events, incident, 'events', 'event')
    norm.normEntities = generate_vector_list(list_entities, incident, 'entities', 'entity')
    norm.normImpacts = generate_vector_list(list_impacts, incident, 'impacts', 'impact')
    return norm
