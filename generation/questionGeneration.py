from nltk import CFG, ChartParser, Production, Nonterminal
from random import choice
from normalization.norm import generate_id_list, generate_name_list
import json


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
          Production(Nonterminal('V1'), ('been', Nonterminal('ATTR'))),
          Production(Nonterminal('V2'), ('noticed', Nonterminal('ATTR'))),
          Production(Nonterminal('V2'), ('registered', Nonterminal('ATTR')))]
    # add wanted attribute as new production
    new_production = Production(Nonterminal('ATTR'), (attribute,))
    bl.append(new_production)
    grammar = CFG(Nonterminal('S'), bl)
    return grammar


def generate_question(attribute):
    parser = ChartParser(generate_grammar(attribute, ))
    gr = parser.grammar()
    return ' '.join(produce(gr, gr.start()))


def get_attribute_name(attr_id, topic):
    id_list = generate_id_list(json.loads(topic)[0], [])
    names = generate_name_list(json.loads(topic)[0], [])
    index = id_list.index(attr_id)
    attribute = names[index]
    return attribute
