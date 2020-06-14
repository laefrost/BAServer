import json
import numpy as np


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
def reverse_norm_incident(norm_incident, sources, events, entities, impacts, user_incident):
    sourcesNI = np.array(norm_incident['normSources'])
    eventsNI = np.array(norm_incident['normEvents'])
    entitiesNI = np.array(norm_incident['normEntities'])
    impactsNI = np.array(norm_incident['normImpacts'])
    print(user_incident)
    rev_incident = user_incident
    rev_incident['sources'] = reverse_attributes(generate_name_list(json.loads(sources)[0], []),
                                                 generate_id_list(json.loads(sources)[0], []),
                                                 np.where(sourcesNI != 0)[0], [], 'source')
    rev_incident['events'] = reverse_attributes(generate_name_list(json.loads(events)[0], []),
                                                generate_id_list(json.loads(events)[0], []),
                                                np.where(eventsNI != 0)[0], [], 'event')
    rev_incident['entities'] = reverse_attributes(generate_name_list(json.loads(entities)[0], []),
                                                  generate_id_list(json.loads(entities)[0], []),
                                                  np.where(entitiesNI != 0)[0], [], 'entity')
    rev_incident['impacts'] = reverse_attributes(generate_name_list(json.loads(impacts)[0], []),
                                                 generate_id_list(json.loads(impacts)[0], []),
                                                 np.where(impactsNI != 0)[0], [], 'impact')
    print(rev_incident)
    return rev_incident


def reverse_attributes(names, ids, indices, reversed_list, keyword):
    list = []
    print(indices)
    for index in indices:
        attribute_list = []
        id = ids[index]
        attribute_list.append(id)
        attribute_list.insert(0, names[index])
        while id[:-2]:
            index_new = ids.index(id[:-2])
            attribute_list.insert(0, names[index_new])
            id = id[:-2]
        attr_dict = {keyword: attribute_list}
        print(attr_dict)
        list.append(attr_dict)
    return list


# generates normalized incident
def normalize_incident(incident, sources, events, entities, impacts):
    list_source = generate_id_list(json.loads(sources)[0], [])
    list_events = generate_id_list(json.loads(events)[0], [])
    list_entities = generate_id_list(json.loads(entities)[0], [])
    list_impacts = generate_id_list(json.loads(impacts)[0], [])

    norm = {'title': incident["title"], 'refId': incident["myId"],
            'normSources': generate_vector_list(list_source, incident, 'sources', 'source'),
            'normEvents': generate_vector_list(list_events, incident, 'events', 'event'),
            'normEntities': generate_vector_list(list_entities, incident, 'entities', 'entity'),
            'normImpacts': generate_vector_list(list_impacts, incident, 'impacts', 'impact')}
    return norm
