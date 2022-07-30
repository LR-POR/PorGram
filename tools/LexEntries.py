import delphin.tdl as tdl

d = {
    'type':'non-uniform-adj-lex',
    'synsem':'SYNSEM.LKEYS.KEYREL.PRED',
    'stem':['estranho','longo'],
    'prefix':'nu-adj'
}

for stem in d['stem']:
     conj = tdl.Conjunction([
          tdl.TypeIdentifier(d['type']),
          tdl.AVM([('STEM', tdl.ConsList(values=[tdl.String(stem)],end=tdl.EMPTY_LIST_TYPE)),
                    (d['synsem'],tdl.String(f'_{stem}_a_rel'))])
     ])
     t = tdl.TypeDefinition(f'{d["prefix"]}-{stem}', conj)
     print(tdl.format(t),'\n')

#python3 ./etc/lex-entries.py > ./etc/ouput.txt