from nltk import CFG, ChartParser, Production, Nonterminal
from random import choice
from normalization.norm import generate_id_list, generate_name_list
import json
import spacy
en_nlp = spacy.load('en_core_web_sm')


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


# context free grammar
def generate_grammar(attribute):
    bl = [Production(Nonterminal('S'), (Nonterminal('HV'),)),
          Production(Nonterminal('HV'), ('Has', Nonterminal('S1'))),
          Production(Nonterminal('HV'), ('Have', Nonterminal('S2'))),
          Production(Nonterminal('S1'), ('there', Nonterminal('V1'))),
          Production(Nonterminal('S2'), ('you', Nonterminal('V2'))),
          Production(Nonterminal('V1'), ('been ', Nonterminal('N1'))),
          Production(Nonterminal('N1'), ('signs of ', Nonterminal('ATTR'))),
          Production(Nonterminal('N1'), ('indications for ', Nonterminal('ATTR'))),
          Production(Nonterminal('V2'), ('noticed', Nonterminal('N1'))),
          Production(Nonterminal('V2'), ('registered', Nonterminal('N1')))]
    # add wanted attribute as new production
    new_production = Production(Nonterminal('ATTR'), (attribute,))
    bl.append(new_production)
    grammar = CFG(Nonterminal('S'), bl)
    return grammar


def generate_counter_grammar(attribute):
    prod = [Production(Nonterminal('S'), (Nonterminal('HV'),)),
            Production(Nonterminal('HV'), ('Are', Nonterminal('S1'))),
            Production(Nonterminal('S1'), ('you', Nonterminal('AD'))),
            Production(Nonterminal('AD'), ('sure', Nonterminal('KONJ'))),
            Production(Nonterminal('AD'), ('certain', Nonterminal('KONJ'))),
            Production(Nonterminal('KONJ'), ('that', Nonterminal('SEN1'))),
            Production(Nonterminal('SEN1'), ('there was no', Nonterminal('N1'))),
            Production(Nonterminal('N1'), ('sign of ', Nonterminal('ATTR'))),
            Production(Nonterminal('N1'), ('involvement of ', Nonterminal('ATTR'))),
            Production(Nonterminal('N1'), ('appearance of ', Nonterminal('ATTR')))]
    new_production = Production(Nonterminal('ATTR'), (attribute,))
    prod.append(new_production)
    grammar = CFG(Nonterminal('S'), prod)
    return grammar


def generate_question(attribute):
    parser = ChartParser(generate_grammar(attribute, ))
    gr = parser.grammar()
    return ' '.join(produce(gr, gr.start()))


def generate_counter_question (attribute):
    parser = ChartParser(generate_counter_grammar(attribute, ))
    gr = parser.grammar()
    return ' '.join(produce(gr, gr.start()))


def get_attribute_name(attr_id, topic):
    id_list = generate_id_list(json.loads(topic)[0], [])
    names = generate_name_list(json.loads(topic)[0], [])
    index = id_list.index(attr_id)
    attribute = names[index]
    return attribute


def generate_mc_question(pos_que):
    doc = en_nlp(pos_que)
    sentence = next(doc.sents)
    coun_que = ''
    for word in sentence:
        if str(word.dep_) == 'aux':
            temp = str(word) + 'n\'t '
            coun_que = coun_que + ' ' + str(temp)
        else:
            coun_que = coun_que + ' ' + str(word) + ' '
    return coun_que

