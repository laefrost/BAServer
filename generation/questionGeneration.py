from nltk import CFG, ChartParser, Production, Nonterminal
import nltk

nltk.download('averaged_perceptron_tagger')
nltk.download('punkt')

from random import choice
from normalization.norm import generate_id_list, generate_name_list
import json
#import spacy
import inflect

inflect = inflect.engine()

#en_nlp = spacy.load('en_core_web_sm')

#nouns = ['lack', 'loss', 'failure']
#adjectives = ['missing', 'missing', 'failing']


def produce(grammar, symbol):
    words = []
    productions = grammar.productions(lhs=symbol)
    production = choice(productions)
    for sym in production.rhs():
        if isinstance(sym, str):
            words.append(sym)
        else:
            words.extend(produce(grammar, sym))
    return words


def get_attribute_name(attr_id, topic):
    id_list = generate_id_list(json.loads(topic)[0], [])
    names = generate_name_list(json.loads(topic)[0], [])
    index = id_list.index(attr_id)
    attribute = names[index]
    return attribute.lower()


def generate_impacts_question(attr, impacts, phase):
    impact = get_attribute_name(attr, impacts)
    parser = ChartParser(generate_impacts_grammar(impact, phase))
    gr = parser.grammar()
    question = {'text': ' '.join(produce(gr, gr.start())), 'answer': 0, 'questionId': 0,
                'attrId': attr,
                'topicId': 4}
    return question


def generate_impacts_grammar(attribute, phase):
    gr = [Production(Nonterminal('S'), (Nonterminal('AUX1'),)),
          Production(Nonterminal('AUX1'), ('Do', Nonterminal('S1'))),
          Production(Nonterminal('S1'), ('you', Nonterminal('V1'))),
          Production(Nonterminal('V1'), ('think', Nonterminal('ART'))),
          Production(Nonterminal('ART'), ('the impact of the incident', Nonterminal('V2'))),
          Production(Nonterminal('END'), ('?',))]
    if phase == 1:
        v2 = Production(Nonterminal('V2'), ('was', Nonterminal('ATTR')))
    else:
        v2 = Production(Nonterminal('V2'), ('was not', Nonterminal('ATTR')))
    attribute = Production(Nonterminal('ATTR'), (attribute, Nonterminal('END')))
    gr.append(v2)
    gr.append(attribute)
    grammar = CFG(Nonterminal('S'), gr)
    return grammar


def generate_entities_question(attr, entities, phase):
    entity = get_attribute_name(attr, entities)
    parser = ChartParser(generate_entities_grammar(entity, phase))
    gr = parser.grammar()
    question = {'text': ' '.join(produce(gr, gr.start())), 'answer': 0, 'questionId': 0,
                'attrId': attr, 'topicId': 3}
    return question


def generate_entities_grammar(attribute, phase):
    gr = [Production(Nonterminal('S'), (Nonterminal('AUX1'),)),
          Production(Nonterminal('AUX1'), ('Do', Nonterminal('S1'))),
          Production(Nonterminal('S1'), ('you', Nonterminal('V1'))),
          Production(Nonterminal('V1'), ('think', Nonterminal('ATTR'))),
          Production(Nonterminal('V3'), ('impacted', Nonterminal('OBJ'))),
          Production(Nonterminal('V3'), ('affected', Nonterminal('OBJ'))),
          Production(Nonterminal('OBJ'), ('by the incident', Nonterminal('END'))),
          Production(Nonterminal('END'), ('?',))]
    if phase == 1:
        v2 = Production(Nonterminal('V2'), ('are', Nonterminal('V3')))
    else:
        v2 = Production(Nonterminal('V2'), ('are not', Nonterminal('V3')))
    attribute = Production(Nonterminal('ATTR'), (attribute, Nonterminal('V2')))
    gr.append(v2)
    gr.append(attribute)
    grammar = CFG(Nonterminal('S'), gr)
    return grammar


def generate_sources_question(attr, parent_attr, sources, phase):
    id = attr
    attribute = get_attribute_name(attr, sources)
    attribute = analyze_numerus(attribute)
    if parent_attr is not None:
        parent_attr = get_attribute_name(parent_attr, sources)
    parser = ChartParser(generate_sources_grammar(attribute, parent_attr, phase))
    gr = parser.grammar()
    question = {'text': ' '.join(produce(gr, gr.start())), 'answer': 0, 'questionId': 0, 'attrId': id,
                'topicId': 1}
    return question


def generate_events_question(attribute, parent_attr, events, phase):
    id = attribute
    attr = get_attribute_name(attribute, events)
    attr = analyze_word_type(attr)
    attr = analyze_numerus(attr)
    if parent_attr is not None:
        parent_attr = get_attribute_name(parent_attr, events)
        parent_attr = analyze_word_type(parent_attr)
    parser = ChartParser(generate_events_grammar(attr, parent_attr, phase))
    gr = parser.grammar()
    question = {'text': ' '.join(produce(gr, gr.start())), 'answer': 0, 'questionId': 0, 'attrId': id,
                'topicId': 2}
    return question


def generate_events_grammar(attribute, parent, phase):
    gr = [Production(Nonterminal('S'), (Nonterminal('AUX1'),)),
          Production(Nonterminal('AUX1'), ('Do', Nonterminal('S1'))),
          Production(Nonterminal('S1'), ('you', Nonterminal('V1'))),
          Production(Nonterminal('V1'), ('think', Nonterminal('ART'))),
          Production(Nonterminal('ATTR'), (attribute, Nonterminal('END'))),
          Production(Nonterminal('END'), ('?',))]
    if parent is not None:
        art = Production(Nonterminal('ART'), ('the', Nonterminal('PAR')))
        par = Production(Nonterminal('PAR'), (parent, Nonterminal('V2')))
    else:
        art = Production(Nonterminal('ART'), ('the', Nonterminal('PAR')))
        par = Production(Nonterminal('PAR'), ('events that caused the incident', Nonterminal('V2')))
    if phase == 1:
        v2 = Production(Nonterminal('V2'), ('included', Nonterminal('ATTR')))
    else:
        v2 = Production(Nonterminal('V2'), ('did not include', Nonterminal('ATTR')))
    gr.append(art)
    gr.append(par)
    gr.append(v2)
    grammar = CFG(Nonterminal('S'), gr)
    return grammar


def generate_sources_grammar(attribute, parent, phase):
    gr = [Production(Nonterminal('S'), (Nonterminal('AUX1'),)),
          Production(Nonterminal('AUX1'), ('Do', Nonterminal('S1'))),
          Production(Nonterminal('S1'), ('you', Nonterminal('V1'))),
          Production(Nonterminal('V1'), ('think', Nonterminal('ART'))),
          Production(Nonterminal('ATTR'), (attribute, Nonterminal('END'))),
          Production(Nonterminal('END'), ('?',))]
    if phase == 1:
        v2 = Production(Nonterminal('V2'), ('included', Nonterminal('ATTR')))
    else:
        v2 = Production(Nonterminal('V2'), ('didn´t include', Nonterminal('ATTR')))
    if parent is None:
        article = Production(Nonterminal('ART'), ('the', Nonterminal('CLS')))
        parent = Production(Nonterminal('CLS'), ('sources', Nonterminal('V2')))
    else:
        article = Production(Nonterminal('ART'), ('the', Nonterminal('PAR')))
        parent = Production(Nonterminal('PAR'), (parent, Nonterminal('V2')))
    gr.append(v2)
    gr.append(article)
    gr.append(parent)
    grammar = CFG(Nonterminal('S'), gr)
    return grammar


def analyze_word_type(attribute):
    attr = nltk.word_tokenize(attribute)
    pos = nltk.pos_tag(attr)
    if len(pos) == 1:
        if pos[0][1] == 'JJ' or pos[0][1] == 'JJR' or pos[0][1] == 'JJS':
            return attribute + ' issues'
    return attribute


def analyze_numerus(attribute):
    vowels = ('a', 'e', 'i', 'o', 'u', 'A', 'E', 'I', 'O', 'U')
    attr = nltk.word_tokenize(attribute)
    pos = nltk.pos_tag(attr)
    for i in range(len(pos)):
        if i < len(pos) - 1:
            if pos[i][1] == 'NN' and pos[i + 1][1] != 'NN':
                if not inflect.singular_noun(pos[i][0]):
                    if pos[0][0].startswith(vowels):
                        return 'an ' + attribute
                    else:
                        return 'a ' + attribute
        else:
            if not inflect.singular_noun(pos[i][0]):
                if pos[0][0].startswith(vowels):
                    return 'an ' + attribute
                else:
                    return 'a ' + attribute
    return attribute
