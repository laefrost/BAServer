class QuestionFrontend():
    def __init__(self, questionId, attributeId, topicId, text, answerRight, answerWrong):
        self.attributeId = attributeId
        self.questionId = questionId
        self.topicId = topicId
        self.text = text
        self.answerRight = answerRight
        self.answerWrong = answerWrong