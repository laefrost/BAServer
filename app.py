from encodings import undefined

from flask import Flask, request, Response, jsonify
from flask_cors import CORS
from flask_mongoengine import MongoEngine

from database.models.QuestionFrontend import QuestionFrontend
from database.models.incident import Incident
from database.models.normUserIncidents import NormUserIncident
from database.models.question import Question
from database.models.questionResponse import QuestionResponse
from database.models.relationship import Relationship
from database.models.sourcesNewStruct import SourceNew
from database.models.userIncident import UserIncident
from database.models.impact import Impact
from database.models.entity import Entity
from database.models.event import Event
from database.models.normIncident import NormIncident
from calculations.calculate import calculateCosine
from normalization.norm import normalizeIncident, normalizeUserIncident, travTest
import json
import numpy as np

app = Flask(__name__)
referenceList = [];

app.config['MONGODB_SETTINGS'] = {
    'DB': "BA-Tool",
    'host': 'mongodb+srv://admin:waschbecken@ba-tool-c4fgc.mongodb.net/test?retryWrites=true&w=majority',
}
db = MongoEngine(app)
CORS(app)


@app.route('/incidents', methods=['GET'])
def get_Incidents():
    incidents = Incident.objects().to_json()
    return Response(incidents, mimetype="application/json", status=200)


@app.route('/incidents', methods=['POST'])
def post_Incident():
    body = request.get_json()
    incident = Incident(**body)
    incidentTemp = Incident.objects.order_by('-myId').first()
    if (incidentTemp is None):
        incident.myId = 0
    else:
        temp = incidentTemp['myId']
        incident.myId = temp + 1;

    incident.save()
    post_NormIncident(incident)
    return Response(incident.to_json(), 200)


@app.route('/incidents/<id>', methods=['DELETE'])
def delete_Incident(id):
    Incident.objects.get(id=id).delete()
    return '', 200


@app.route('/norm_incidents', methods=['GET'])
def get_NormIncidents():
    incidents = NormIncident.objects().to_json()
    return incidents


@app.route('/norm_incidents', methods=['POST'])
def post_NormIncident(incident):
    sources = get_Sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    normIncident = normalizeIncident(incident, sources, events, entities, impacts)
    normIncident.save()
    return Response(normIncident.to_json(), 200)

@app.route('/norm_UserIncidents', methods=['POST'])
def post_NormUserIncident(incident):
    sources = get_Sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    normIncident = normalizeUserIncident(incident, sources, events, entities, impacts)
    normIncident.save()
    return normIncident

@app.route('/norm_incidents/<id>', methods=['DELETE'])
def delete_NormIncident(id):
    NormIncident.objects.get(id=id).delete()
    return '', 200


@app.route('/user_incidents', methods=['GET'])
def get_userIncidents():
    incidents = UserIncident.objects().to_json()
    return Response(incidents, mimetype="application/json", status=200)


@app.route('/user_incidents', methods=['POST'])
def post_userIncident():
    body = request.get_json()
    userIncident = UserIncident(**body)
    incidentTemp = UserIncident.objects.order_by('-myId').first()
    if (incidentTemp is None):
        userIncident.myId = 0
    else:
        temp = incidentTemp['myId']
        userIncident.myId = temp + 1

    sources = get_Sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    #normUserIncident = normalizeIncident(userIncident, sources, events, entities, impacts)
    normUserIncident = post_NormUserIncident(userIncident)
    predefIncNorm = get_NormIncidents()
    questionIds = calculateCosine(normUserIncident, predefIncNorm, sources, events, entities, impacts)

    questions= get_questions(questionIds)

    questionResponse = {}
    questionResponse['id'] = userIncident.myId
    questionResponse['questions'] = questions
    userIncident.save()
    print(questionResponse)
    return questionResponse


@app.route('/user_incidents/<id>', methods=['DELETE'])
def delete_userIncident(id):
    UserIncident.objects.get(id=id).delete()
    return '', 200


@app.route('/sources', methods=['GET'])
def get_Sources():
    sources = SourceNew.objects().to_json()
    return sources


@app.route('/sources', methods=['POST'])
def post_Sources():
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


#@app.route('/questions', methods=['GET'])
#def get_questions(id):
    #print("getQuestions")
    #print(id)
   # questions = Relation.objects(topicId=id).to_json()
    #return json.loads(questions)

def get_questions(questionIds):
    questionList = []
    for element in questionIds['sources']:
        relations = Relationship.objects(topicId=1, attributeId=element).to_json()
        rel = json.loads(relations)
        for el in rel:
            print(questionList)
            temp = Question.objects(questionId=el['questionId'])
            for t in temp:
                question = {}
                question['questionId'] = t['questionId']
                question['topicId'] = 1
                question['attributeId'] = element
                question['text'] = t['text']
                question['answer'] = 0
                questionList.append(question)

    return questionList

@app.route('/questions', methods=['POST'])
def post_question():
    body = request.get_json()
    q = Question(**body)
    qTemp = Question.objects.order_by('-questionId').first()
    if (qTemp is None):
        q.questionId = 0
    else:
        temp = qTemp['questionId']
        q.questionId = temp + 1
    print(q)
    q.save()
    return Response(q.to_json(), 200)

@app.route('/relations', methods=['POST'])
def post_relation():
    body = request.get_json()
    r = Relationship(**body)
    r.save()
    return Response(r.to_json(), 200)

@app.route('/answer', methods=['POST'])
def post_answer():
    print("answer")
    body = request.get_json()
    print(body)
    userNormIncident = get_normUserIncident(body['id'])
    print(userNormIncident)
    sources = get_Sources()
    events = get_events()
    entities = get_entities()
    impacts = get_impacts()
    predefIncNorm = get_NormIncidents()
    listSource = travTest(json.loads(sources)[0], [])
    listEvents = travTest(json.loads(events)[0], [])
    listEnities = travTest(json.loads(entities)[0], [])
    listImpacts = travTest(json.loads(impacts)[0], [])
    s = userNormIncident['normSources']
    ev = userNormIncident['normEvents']
    en = userNormIncident['normEntities']
    im = userNormIncident['normImpacts']
    for answer in body['answers']:
        print(answer)
        if answer['topicId'] == 1:
            index = listSource.index(answer['attributeId'])
            print(index)
            s[index] = 1 * answer['answer']
        elif answer['topicId'] == 2:
            index = listEvents.index(answer['attributeId'])
            print(index)
            ev[index] = 1 * answer['answer']
        elif answer['topicId'] == 3:
            index = listEnities.index(answer['attributeId'])
            print(index)
            en[index] = 1 * answer['answer']
        elif answer['topicId'] == 2:
            index = listImpacts.index(answer['attributeId'])
            print(index)
            im[index] = 1 * answer['answer']

    u = NormUserIncident()
    u.title = userNormIncident["title"]
    u.refId = userNormIncident["refId"]
    u.normSources = s
    u.normEvents = ev
    u.normEntities = en
    u.normImpacts = im
    questionIds = calculateCosine(u, predefIncNorm, sources, events, entities, impacts)
    print(questionIds)
    #if null the done -> return 0
    #if contains questions -> ask questions again to user
    return body

def get_normUserIncident(id):
    incidents = NormUserIncident.objects(refId=id).to_json()
    return json.loads(incidents)[0]

app.run()
