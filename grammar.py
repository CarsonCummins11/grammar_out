from typing import List, Dict, Set


def is_class(token: str) -> bool:
    return token.startswith('$$$') and token.endswith('$$$')

def is_epsilon(token: str) -> bool:
    return token == '###'

def make_class(token: str) -> str:
    return f'$$${token}$$$'

class Grammar:
    def __init__(self, productions: Dict[str, List[List[str]]]):
        print(productions)
        self.productions = productions
        self.classes = set(productions.keys())
        self.follow_sets = {} # token -> follow set cache
        self.first_sets = {}  # token -> first set cache
        self.cache_is_saturated = False
        # ensure everything is defined
        for class_name, production in productions.items():
            assert production
            assert class_name
    @staticmethod
    def from_string(grammar: str):
        productions:Dict[str, List[List[str]]] = {}
        for line in grammar.split('\n'):
            if not line:
                continue
            class_name, production = [x.strip() for x in line.split('->')]
            cases = production.split('|||')
            for case in cases:
                rule = [x.strip() for x in case.split()]
                if class_name in productions:
                    productions[class_name].append(rule)
                else:
                    productions[class_name] = [rule]
        return Grammar(productions)
    def first(self, token: str) -> Set[str]:
        # computes the first set for a given token
        if token in self.first_sets or self.cache_is_saturated:
            return self.first_sets.get(token, set())
        first_set = set()
        if is_class(token):
            for case in self.productions[token[3:-3]]:
                if is_epsilon(case[0]):
                    if len(case) > 1:
                        first_set.update(self.first(case[1]))
                    else:
                        print(f'epsilon starts a case of {token}, computing follow set')
                        first_set.update(self.follow(token))
                else:
                    first_set.update(self.first(case[0]))
        elif is_epsilon(token):
            raise ValueError('Cannot compute first of epsilon. Are there two epsilon tokens in sequence in a production?')
        else:
            # token is terminal
            first_set.add(token)
        
        self.first_sets[token] = first_set
        return first_set

    def follow(self, token: str) -> Set[str]:
        # computes the follow set for a given token
        # this is gonna be slow asf i bet there's a faster way
        if token in self.follow_sets or self.cache_is_saturated:
            return self.follow_sets.get(token, set())
        follow_set = set()
        for class_name, rule in self.productions.items():
            class_name = make_class(class_name)
            for case in rule:
                for i, rtoken in enumerate(case):
                    if rtoken == token:
                        print(f'found {token} in {case} of {class_name}')
                        if i == len(case) - 1:
                            print(f'{token} is the last token in the case, computing follow set of {class_name}')
                            follow_set.update(self.follow(class_name))
                        else:
                            print(f'{token} is not the last token in the case, computing first of next token {case[i+1]}')
                            follow_set.update(self.first(case[i+1]))
        if follow_set:
            self.follow_sets[token] = follow_set
        return follow_set
    
    def compute_first_sets(self):
        for class_name in self.classes:
            self.first(class_name)
    def compute_follow_sets(self, vocab: Set[str]):
        for tok in vocab:
            self.follow(tok)

def test():
    g1 = '''
A -> $$$B$$$ $$$C$$$
B -> $$$D$$$ ||| $$$E$$$
C -> !
D -> Hello ||| ###
E -> World
'''
    print(Grammar.from_string(g1).follow('$$$B$$$'))

if __name__ == '__main__':
    test()