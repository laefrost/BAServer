import json
from database.models.normIncident import NormIncident
from database.models.normUserIncidents import NormUserIncident


def travTest(elements, result):
    for element in elements['elements']:
        t = 'elements'
        if t in element:
            id = element.get("id")
            result.append(id)
            travTest(element, result)
        else:
            result.append(element.get("id"))
    return result


def generateReferanceListSource(list, incident):
    refList = {}
    for i in range(len(list)):
        if (incident["sources"] is not None and len(incident["sources"])>0):
            for source in incident["sources"]:
                sourceList = source["source"]
                if (len(sourceList) != 0):
                    id = sourceList[-1]
                    if id == list[i]:
                        refList[i] = 1
                    else:
                        if refList.get(i)!=1:
                            refList[i]= 0
                else:
                    refList[i] = 0
        else:
            refList[i] = 0
    result = [*refList.values()]
    return result

def generateReferanceListEvent(list, incident):
    refList = {}

    for i in range(len(list)):
        if (incident["events"] is not None and len(incident["events"]) > 0):
            for element in incident["events"]:
                evList = element["event"]
                if (len(evList) != 0):
                    id = evList[-1]
                    if id == list[i]:
                        refList[i] = 1
                    else:
                        if refList.get(i)!=1:
                            refList[i]= 0
                else:
                    refList[i]=0
        else:
            refList[i] = 0
    result = [*refList.values()]
    return result

def generateReferanceListEntity(list, incident):
    refList = {}

    for i in range(len(list)):
        if (incident["entities"] is not None and len(incident["entities"]) > 0):
            for element in incident["entities"]:
                enList = element["entity"]
                if (len(enList) != 0):
                    id = enList[-1]
                    if id == list[i]:
                        refList[i] = 1
                    else:
                        if refList.get(i)!=1:
                            refList[i]= 0
                else:
                    refList[i] = 0
        else:
            refList[i] = 0
    result = [*refList.values()]
    return result

def generateReferanceListImpact(list, incident):
    refList = {}

    for i in range(len(list)):
        if (incident["impacts"] is not None and len(incident["impacts"]) > 0):
            for element in incident["impacts"]:
                impactList = element["impact"]
                if (len(impactList) != 0):
                    id = impactList[-1]
                    if id == list[i]:
                        refList[i] = 1
                    else:
                        if refList.get(i)!=1:
                            refList[i]= 0
                else:
                    refList[i]= 0
        else:
            refList[i] = 0
    result = [*refList.values()]
    return result

def normalizeIncident(incident, sources, events, entities, impacts):
    listSource = travTest(json.loads(sources)[0], [])
    listEvents = travTest(json.loads(events)[0], [])
    listEnities = travTest(json.loads(entities)[0], [])
    listImpacts = travTest(json.loads(impacts)[0], [])

    norm = NormIncident()
    norm.title = incident["title"]
    norm.refId = incident["myId"]
    norm.normSources = generateReferanceListSource(listSource, incident)
    norm.normEvents = generateReferanceListEvent(listEvents, incident)
    norm.normEntities = generateReferanceListEntity(listEnities, incident)
    norm.normImpacts = generateReferanceListImpact(listImpacts, incident)
    #print(norm.to_json())
    return norm


def normalizeUserIncident(incident, sources, events, entities, impacts):
    listSource = travTest(json.loads(sources)[0], [])
    listEvents = travTest(json.loads(events)[0], [])
    listEnities = travTest(json.loads(entities)[0], [])
    listImpacts = travTest(json.loads(impacts)[0], [])

    norm = NormUserIncident()
    norm.title = incident["title"]
    norm.refId = incident["myId"]
    norm.normSources = generateReferanceListSource(listSource, incident)
    norm.normEvents = generateReferanceListEvent(listEvents, incident)
    norm.normEntities = generateReferanceListEntity(listEnities, incident)
    norm.normImpacts = generateReferanceListImpact(listImpacts, incident)
    #print(norm.to_json())
    return norm