from scipy import spatial
import json
from operator import itemgetter
from normalization.norm import travTest

def calculateCosine(normUserIncident, predefIncNorms, sources, events, entities, impacts):
    print("calculateCosine")
    cosineList = []
    normIncidents = json.loads(predefIncNorms)
    print(normIncidents)
    dataUser = normUserIncident.normSources + normUserIncident.normEvents +normUserIncident.normEntities +normUserIncident.normImpacts
    for incident in normIncidents:
        dataPreDef = incident["normSources"] + incident["normEvents"] +incident["normEntities"] +incident["normImpacts"]
        result = 1 - spatial.distance.cosine(dataUser, dataPreDef)
        cosineList.append(result)
    print(cosineList)
    index, value = max(enumerate(cosineList), key=itemgetter(1))
    print("most Sim Incident")
    print(normIncidents[index])
    ids = compareLists(normUserIncident, normIncidents[index], sources, events, entities, impacts)
    return ids

#ändern um Refinement möglich zu machen
def compareLists(normUserIncident, normIncident, sources, events, entities, impacts):
    print("compareLists")
    diffSourceIndex = []
    diffEventIndex = []
    diffEntityIndex = []
    diffImpactIndex = []
    response = {}
    for i in range(len(normIncident["normSources"])):
        if normIncident["normSources"][i] == 1 and normIncident["normSources"][i] != normUserIncident["normSources"][i]:
           diffSourceIndex.append(i)

    for i in range(len(normIncident["normEvents"])):
        if normIncident["normEvents"][i] == 1 and normIncident["normEvents"][i] != normUserIncident["normEvents"][i]:
           diffEventIndex.append(i)

    for i in range(len(normIncident["normEntities"])):
        if normIncident["normEntities"][i] == 1 and normIncident["normEntities"][i] != normUserIncident["normEntities"][i]:
           diffEntityIndex.append(i)

    for i in range(len(normIncident["normImpacts"])):
        if normIncident["normImpacts"][i] == 1 and normIncident["normImpacts"][i] != normUserIncident["normImpacts"][i]:
           diffImpactIndex.append(i)
    print("diffSource")
    print(diffSourceIndex)
    print("diffEvent")
    print(diffEventIndex)
    print("diffEntity")
    print(diffEntityIndex)
    print("diffImpact")
    print(diffImpactIndex)

    sourcesId = getIds(diffSourceIndex, sources)
    eventsId = getIds(diffEventIndex, events)
    entitiesId = getIds(diffEntityIndex, entities)
    impactsId = getIds(diffImpactIndex, impacts)
    response['sources'] = sourcesId
    response['events'] = eventsId
    response['entities'] = entitiesId
    response['impacts'] = impactsId
    print("response")
    print(response)
    return response

def getIds(indexList, category):
    idList = travTest(json.loads(category)[0], [])
    ids = []
    for index in indexList:
        ids.append(idList[index])
    return ids

