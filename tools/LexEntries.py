import delphin.tdl as tdl
import json
import sys

'''
este script recebe como input um json com os seguintes campos:

    exemplo = {
        'type':'non-uniform-adj-lex',
        'synsem':'SYNSEM.LKEYS.KEYREL.PRED',
        'stem':['estranho','longo'],
        'prefix':'nu-adj'
    }

o exemplo acima tem o seguinte output:

    nu-adj-estranho := non-uniform-adj-lex &
    [ STEM < "estranho" >,
        SYNSEM.LKEYS.KEYREL.PRED "_estranho_a_rel" ]. 

    nu-adj-longo := non-uniform-adj-lex &
    [ STEM < "longo" >,
        SYNSEM.LKEYS.KEYREL.PRED "_longo_a_rel" ]. 

exemplo de uso:
~/PorGram$ python3 path/input.json < ./tools/lex-entries.py > path/ouput.txt

'''


def main(path):
    print('ok')
    f = open(path)
    d = json.load(f)
    for stem in d['stem']:
        conj = tdl.Conjunction([
            tdl.TypeIdentifier(d['type']),
            tdl.AVM([('STEM', tdl.ConsList(values=[tdl.String(stem)],end=tdl.EMPTY_LIST_TYPE)),
                        (d['synsem'],tdl.String(f'_{stem}_a_rel'))])
        ])
        t = tdl.TypeDefinition(f'{d["prefix"]}-{stem}', conj)
        print(tdl.format(t),'\n')

if __name__ == "__main__":
    if len(sys.argv) == 1:
       sys.exit(main(sys.argv[0]))
