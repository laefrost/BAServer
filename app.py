from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_mongoengine import MongoEngine
from database.models.incident import Incident
from database.models.normUserIncidents import NormUserIncident
from database.models.question import Question
from database.models.relationship import Relationship
from database.models.sourcesNewStruct import SourceNew
from database.models.userIncident import UserIncident
from database.models.impact import Impact
from database.models.entity import Entity
from database.models.event import Event
from database.models.normIncident import NormIncident
from calculations.calculate import calculate_cosine
from normalization.norm import normalize_incident, generate_id_list, generate_name_list
from generation.questionGeneration import generate_question, get_attribute_name
import json

app = Flask(__name__)
referenceList = [];

app.config['MONGODB_SETTINGS'] = {
    'DB': "BA-Tool",
    'host': 'mongodb+srv://admin:waschbecken@ba-tool-c4fgc.mongodb.net/test?retryWrites=true&w=majority',
}
db = MongoEngine(app)
CORS(app)

# reference incidents


@app.route('/incidents', methods=['GET'])
def get_incidents():
    incidents = Incident.objects().to_json()
    return Response(incidents, mimetype="application/json", status=200)


@app.route('/incidents', methods=['POST'])
def post_incident():
    body = request.get_json()
    incident = Incident(**body)
    first_incident = Incident.objects.order_by('-myId').first()
    if first_incident is None:
        incident.myId = 0
    else:
        temp = first_incident['myId']
        incident.myId = temp + 1;
    incident['transmittedBy'] = 'admin'
    incident.save()
    post_norm_ref_incident(incident)
    return Response(incident.to_json(), 200)


@app.route('/incidents/<id>', methods=['DELETE'])
def delete_incident(incident_id):
    Incident.objects.get(id=incident_id).delete()
    return '', 200


@app.route('/transferIncidents', methods=['POST'])
def post_StagedIncident():
    body = request.get_json()
    incident = Incident()
    incident['title'] = body['title']
    incident['sources'] = body['sources']
    incident['events'] = body['events']
    incident['entities'] = body['entities']
    incident['impacts'] = body['impacts']
    incident['transmittedBy'] = 'user'
    incidentTemp = Incident.objects.order_by('-myId').first()
    if (incidentTemp is None):
        incident.myId = 0
    else:
        incident.myId = incidentTemp['myId'] + 1;
    incident.save()
    post_norm_ref_incident(incident)
    delete_user_incident(body['myId'])
    return Response(incident.to_json(), 200)


# normalized reference incidents


@app.route('/norm_incidents', methods=['GET'])
def get_norm_ref_incidents():
    incidents = NormIncident.objects().to_json()
    return incidents


@app.route('/norm_incidents', methods=['POST'])
def post_norm_ref_incident(incident):
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    norm_incident.save()
    return Response(norm_incident.to_json(), 200)


@app.route('/norm_incidents/<id>', methods=['DELETE'])
def delete_norm_incident(incident_id):
    NormIncident.objects.get(id=incident_id).delete()
    return '', 200

# user incidents


@app.route('/user_incidents', methods=['GET'])
def get_user_incidents():
    incidents = UserIncident.objects().to_json()
    return Response(incidents, mimetype="application/json", status=200)


@app.route('/user_incidents', methods=['POST'])
def post_user_incident():
    body = request.get_json()
    user_incident = UserIncident(**body)
    first_incident = UserIncident.objects.order_by('-myId').first()
    if first_incident is None:
        user_incident.myId = 0
    else:
        temp = first_incident['myId']
        user_incident.myId = temp + 1

    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    norm_user_incident = post_norm_user_incident(user_incident, sources, events, entities, impacts)
    norm_ref_incidents = get_norm_ref_incidents()
    question_ids = calculate_cosine(norm_user_incident, norm_ref_incidents, sources, events, entities, impacts, 1)
    questions = get_questions(question_ids)
    question_response = {'id': user_incident.myId, 'questions': questions}
    user_incident.save()
    return question_response


@app.route('/user_incidents/<id>', methods=['DELETE'])
def delete_user_incident(incident_id):
    UserIncident.objects(myId=incident_id).delete()
    NormUserIncident.objects(refId=incident_id).delete()
    return '', 200

# normalized user incident


@app.route('/norm_UserIncidents', methods=['POST'])
def post_norm_user_incident(incident, sources, events, entities, impacts):
    norm_incident = normalize_incident(incident, sources, events, entities, impacts)
    norm_incident.save()
    return norm_incident


def delete_norm_user_incident(incident_id):
    NormUserIncident.objects.get(refId=incident_id).delete()
    return '', 200


def get_norm_user_incident(id):
    incidents = NormUserIncident.objects(refId=id).to_json()
    return json.loads(incidents)[0]

# get topics / attributes


@app.route('/sources', methods=['GET'])
def get_sources():
    sources = SourceNew.objects().to_json()
    return sources


@app.route('/sources', methods=['POST'])
def post_sources():
    body = request.get_json()
    newSource = SourceNew(**body).save()
    return Response(newSource.to_json(), 200)


@app.route('/impacts', methods=['GET'])
def get_impacts():
    impacts = Impact.objects().to_json()
    return impacts


@app.route('/events', methods=['GET'])
def get_events():
    events = Event.objects().to_json()
    return events


@app.route('/entities', methods=['GET'])
def get_entities():
    entities = Entity.objects().to_json()
    return entities

# questions


@app.route('/questions', methods=['POST'])
def post_question():
    body = request.get_json()
    q = Question()
    first_question = Question.objects.order_by('-questionId').first()
    if first_question is None:
        q.questionId = 0
    else:
        temp = first_question['questionId']
        q.questionId = temp + 1
    q.text = body['text']
    post_relation(q.questionId, body)
    q.save()
    return Response(q.to_json(), 200)


# toDo: shorten it
@app.route('/relations', methods=['POST'])
def post_relation(question_id, temp):
    for source in temp['sources']:
        t = source['source']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 1, 'attributeId': t[-1]}
            re = Relationship(**r)
            re.save()
    for event in temp['events']:
        t = event['event']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 2, 'attributeId': t[-1]}
            re = Relationship(**r)
            re.save()
    for entity in temp['entities']:
        t = entity['entity']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 3, 'attributeId': t[-1]}
            re = Relationship(**r)
            re.save()
    for impact in temp['impacts']:
        t = impact['impact']
        if len(t) != 0:
            r = {'questionId': question_id, 'topicId': 4, 'attributeId': t[-1]}
            re = Relationship(**r)
            re.save()
    return Response(re.to_json(), 200)


# get all questions that answer attribute
def get_questions(ids):
    result = []
    copy_ids = set()
    for element in ids['sources']:
        if element not in copy_ids:
            result.append(get({}, element, ids['sources'], 1, copy_ids))
    copy_ids = set()
    for element in ids['events']:
        if element not in copy_ids:
            result.append(get({}, element, ids['events'], 2, copy_ids))
    copy_ids = set()
    for element in ids['entities']:
        if element not in copy_ids:
            result.append(get({}, element, ids['entities'], 3, copy_ids))
    copy_ids = set()
    for element in ids['impacts']:
        if element not in copy_ids:
            result.append(get({}, element, ids['impacts'], 4, copy_ids))
    return result


def get(result, attr_id, ids, topic_id, copy_ids):
    relations = Relationship.objects(attributeId=attr_id, topicId=topic_id)
    result['questions'] = []
    result['children'] = []
    question = generate_generic_question(attr_id, topic_id)
    result['questions'].append(question)
    copy_ids.add(attr_id)
    for r in relations:
        temp = Question.objects(questionId=r['questionId']).to_json()
        temp = json.loads(temp)
        for t in temp:
            q = generate_specific_question(t, r['attributeId'], topic_id)
            result['questions'].append(q)
    for element in ids:
        if element[:-2] == attr_id:
            copy_ids.add(element)
            result['children'].append(get({}, element, ids, topic_id, copy_ids))
    if len(result['children']) == 0:
        del result['children']
    return result


def generate_generic_question(attr_id, topic_id):
    attribute = "test"
    if topic_id == 1:
        sources = get_sources()
        attribute = get_attribute_name(attr_id, sources)
    if topic_id == 2:
        events = get_events()
        attribute = get_attribute_name(attr_id, events)
    if topic_id == 3:
        entities = get_entities()
        attribute = get_attribute_name(attr_id, entities)
    if topic_id == 4:
        impacts = get_impacts()
        attribute = get_attribute_name(attr_id, impacts)
    question = {'text': generate_question(attribute), 'answer': 0, 'questionId': 0, 'attrId': attr_id,
                'topicId': topic_id}
    if attr_id[:-2]:
        question['parentId'] = attr_id[:-2]
    return question


def generate_specific_question(q, attribute_id, topic_id):
    question = {'text': q['text'], 'answer': 0, 'questionId': q['questionId'], 'attrId': attribute_id,
                'topicId': topic_id}
    if attribute_id[:-2]:
        question['parentId'] = attribute_id[:-2]
    return question

# handle response from frontend after user answered questions


@app.route('/answer', methods=['POST'])
def post_answer():
    print("answer")
    body = request.get_json()
    user_norm_incidents = get_norm_user_incident(body['id'])
    sources = get_sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    ref_norm_incidents = get_norm_ref_incidents()
    listSource = generate_id_list(json.loads(sources)[0], [])
    listEvents = generate_id_list(json.loads(events)[0], [])
    listEnities = generate_id_list(json.loads(entities)[0], [])
    listImpacts = generate_id_list(json.loads(impacts)[0], [])
    s = user_norm_incidents['normSources']
    ev = user_norm_incidents['normEvents']
    en = user_norm_incidents['normEntities']
    im = user_norm_incidents['normImpacts']

    for answer in body['answers']:
        if answer['topicId'] == 1:
            s[listSource.index(answer['attributeId'])] = answer['value']
        elif answer['topicId'] == 2:
            ev[listEvents.index(answer['attributeId'])] = answer['value']
        elif answer['topicId'] == 3:
            en[listEnities.index(answer['attributeId'])] = answer['value']
        elif answer['topicId'] == 4:
            im[listImpacts.index(answer['attributeId'])] = answer['value']

    u = NormUserIncident()
    u.title = user_norm_incidents["title"]
    u.refId = user_norm_incidents["refId"]
    u.normSources = s
    u.normEvents = ev
    u.normEntities = en
    u.normImpacts = im
    NormUserIncident.objects.get(refId=u['refId']).delete()
    u.save()
    question_ids = calculate_cosine(u, ref_norm_incidents, sources, events, entities, impacts, 2)
    print(question_ids)
    # if questionsId = 0 -> post userIncident with reference Incident
    # reverse norm incident
    questions = get_questions(question_ids)
    question_response = {'id': u.refId, 'questions': questions}
    print(question_response)
    return question_response


app.run()
