from conllu import parse
import joblib


DEPRELS = ['nsubj','obj','iobj','xcomp','ccomp','csubj','expl','nsubj:pass','aux:pass']

## Funçoes auxiliares

def binary_search(x,l):
    """
    Esse algorítmo é o algorítmo de busca binária, mas ele retorna qual o índice o qual devo colocar o elemento para que a lista permaneça ordenada.
    Input: elemento x e lista l
    Output: Índice em que o elemento deve ser inserido para manter a ordenação da lista
    """
    lo = 0 # Cota inferior inicial (Lower bound)
    up = len(l) # Cota superior inicial (Upper bound)
    while lo < up:
        mid = int((lo+up)/2) #Ponto Médio 
        if l[mid] < x:
            lo = mid + 1
        else:
            up = mid
    return up

def convert_token_to_relation(sentence,token):
    """
    Converte um objeto do tipo token da biblioteca conllu em um objeto do tipo Relation criado aqui
    """
    return Relation(sentence,token)


class Relation:
    """
    Objeto do tipo relation, tem basicamente as informações do token e também de seus filhos que nos interessam (case e mark)
    """
    def __init__(self,sentence,token):
        self.token = token['form']
        self.lemma = token['lemma']
        self.deprel = token['deprel']
        self.upos = token['upos']
        self.metadata=token['feats']
        self.relation = []
        son_tokens = get_son_tokens(sentence,token)
        if son_tokens != []:
            for son_token in son_tokens:
                if son_token['deprel'] in ('case','mark'):
                    self.relation.append(convert_token_to_relation(sentence,son_token))
  
        
    def __str__(self):
        return f'[{str(self.lemma)},{str(self.deprel)},{str(self.upos)}]'
    def __repr__(self):
        return f'[{str(self.lemma)},{str(self.deprel)},{str(self.upos)}]'
    

class Valence:
    """
    Objeto do tipo valencia, que guarda as infos específicas de um determinado verbo em uma determinada sentença, como seu xcomp, ccomp, obj etc. caso haja.
    Possui um método print para imprimir as informaçoes da valência do verbo.
    """
    def __init__(self,
                 token,
                 lemma=None,
                 metadata=None, 
                 xcomp=None,
                 ccomp=None,
                 obj=None,
                 iobj=None,
                 expl=None,
                 nsubj=None,
                 csubj=None,
                 nsubj_pass=None,
                 aux_pass = None,
                 example=None,
                 rel_set = None):
        
        self.token = token
        self.lemma = lemma
        self.metadata = metadata
        self.xcomp = xcomp
        self.ccomp = ccomp
        self.obj = obj
        self.iobj = iobj
        self.expl = expl
        self.nsubj = nsubj
        self.csubj = csubj
        self.nsubj_pass = nsubj_pass
        self.aux_pass = aux_pass
        self.example = example
        self.rel_set = rel_set
        
        
    def __repr__(self):
        s = '<'
        for val in self.rel_set:
            s += f'{val},'
        s = s[:-1] + '>'
        return s
    
    def __str__(self):
        s = '<'
        for val in self.rel_set:
            s += f'{val},'
        s = s[:-1] + '>'
        return s
    
    def print(self):
        verb = f'{self.lemma}'
        mdata = ''
        for key in ['Mood','Number','Person','Tense','VerbForm']:
            if key in self.metadata:
                mdata+=f'+{key}:{self.metadata[key]}'
        mdata = mdata + " "
        verb+=mdata
        if self.xcomp is not None:
            val = list(self.xcomp.keys())[0]
            if self.xcomp[val].upos in ('VERB'):
                xcomp = f"xcomp {val}+{self.xcomp[val].lemma}"
                for key in ['Mood','Number','Person','Tense','VerbForm']:
                    if key in self.xcomp[val].metadata:
                        xcomp += f'+{key}:{self.xcomp[val].metadata[key]}'
                xcomp += ' '
                for t in self.xcomp[val].relation:
                    xcomp += f'{t.deprel}+{t.upos}+{t.lemma} '

            else:
                xcomp = f"xcomp "
            verb+=xcomp
        #if self.ccomp is not None:
            #val = list(self.ccomp.keys())[0]
            #ccomp = f'ccomp {val}+{self.ccomp[val].deprel}+{self.ccomp[val].upos}+{self.ccomp[val].lemma} '
        #else:
            #ccomp = f'ccomp '
            #verb+=ccomp
        if self.ccomp is not None:
            val = list(self.ccomp.keys())[0]
            if self.ccomp[val].upos in ('VERB'):
                ccomp = f"ccomp {val}+{self.ccomp[val].lemma}"
                for key in ['Mood','Number','Person','Tense','VerbForm']:
                    if key in self.ccomp[val].metadata:
                        ccomp += f'+{key}:{self.ccomp[val].metadata[key]}'
                ccomp += ' '
                for t in self.ccomp[val].relation:
                    ccomp += f'{t.deprel}+{t.upos}+{t.lemma} '

            else:
                ccomp = f"ccomp "
            verb+=ccomp
        if self.obj is not None:
            if 'ADP' in self.obj.keys():
                if self.obj['ADP'].deprel == 'case':
                    verb += f"obj case+ADP+{self.obj['ADP'].lemma} "
                else:
                    verb += "obj "
            else:
                verb += "obj "
        if self.iobj is not None:
            if 'ADP' in self.iobj.keys():
                if self.iobj['ADP'].deprel == 'case':
                    verb += f"iobj case+ADP+{self.iobj['ADP'].lemma} "
                else:
                    verb += 'iobj '
            else:
                verb += 'iobj '
        if self.nsubj is not None:
            verb += f'nsubj '
        if self.csubj is not None:
            verb += 'csubj '
        if self.nsubj_pass is not None:
            verb += 'nsubj:pass '
        if self.aux_pass is not None:
            if 'AUX' in self.aux_pass.keys():
                aux = f"aux:pass:{self.aux_pass['AUX'].lemma}"
                for key in ['Mood','Number','Person','Tense','VerbForm']:
                    if key in self.aux_pass['AUX'].metadata:
                        aux += f"+{key}:{self.aux_pass['AUX'].metadata[key]}" 
                aux += ' '
            else:
                aux += 'aux:pass '
            verb += aux
                
        if self.expl is not None:
            if 'PRON' in self.expl.keys():
                expl = f"PRON+{self.expl['PRON'].token}+"
                for key in ['Case','Gender','Number','Person','PronType']:
                    if key in self.expl['PRON'].metadata:
                        expl+=f"{self.expl['PRON'].metadata[key]}+"
                expl = expl[:-1]
                verb += expl
        return verb
            

class Verb:
    def __init__(self,lemma=None, valences = []):
        self.lemma = lemma
        self.valences = valences
        
    def __repr__(self):
        return self.lemma
    
    def __str__(self):
        return self.lemma
    
    def add_valence(self,valence):
        if valence.lemma != self.lemma:
            raise TypeError("Not same lemma")
        self.valences.append(valence)

    def print(self):
        print_output = []
        for valence in self.valences:
            print_output.append(valence.print())
        print_output = list(set(print_output))
        s = ''
        for t in print_output:
            s+=t + "\n"
        return s
    #def __repr__(self):
        #s = f"{lemma}:{self.metadata['mood']}+{self.metadata['Number']}+{self.metadata['Person']}+{self.metadata['Tense']}+{self.metadata['VerbForm']}\n"
        #if rels in self.rel.keys():
            
            
            
        
        #return None



## FUNÇÕES BÁSICAS
        

def get_root_index(sentence):
    for token in sentence:
        if token['deprel'] == 'root':
            return sentence.index(token)
        
def get_verbs_index(sentence):
    return [sentence.index(x) for x in sentence if x['upos'] == 'VERB']
        
        
def get_son_tokens(sentence,
                   token):
    token_id = token['id']
    tokens = [t for t in sentence if t['head'] == token_id]
    return tokens

def recover_verbs_valences(sentence,
                           with_lemmas=False):
    verbs = get_verbs_index(sentence)
    if with_lemmas:
        dic = {sentence[x]['lemma']:[(y['deprel'],y['lemma']) for y in get_son_tokens(sentence,sentence[x]) if y['deprel'] not in DEPRELS] for x in verbs}
        return dic
    dic = {sentence[x]['lemma']:[y['deprel'] for y in get_son_tokens(sentence,sentence[x]) if y['deprel']  in DEPRELS] for x in verbs} 
    return dic

def get_rel_set(sentence,token):
    tokens = get_son_tokens(sentence,token)
    rel_set = [x['deprel'] for x in tokens if x['deprel'] in DEPRELS and x['deprel'] != []]
    rel_set_aux = [x['id'] for x in tokens if x['deprel'] in DEPRELS and x['deprel'] != []]
    token_id = token['id']
    i = binary_search(token_id,rel_set_aux)
    rel_set = rel_set[:i] + ['VERB'] + rel_set[i:]
    return rel_set


## FUNÇÕES PARA EXTRAÇÃO


def get_deprel(sentence,token,deprel):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if deprel not in son_tokens_deprel:
        return None
    else:
        deprels = [x for x in son_tokens if x['deprel'] == deprel]
        for deprel_ in deprels:
            result_dic[deprel_['upos']] = Relation(sentence,deprel_)
        return result_dic

def get_obj(sentence,token, iobj = False):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if iobj:
        if 'iobj' not in son_tokens_deprel:
            return None
        else:
            iobjs = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'iobj']
            for iobj_ in iobjs:
                #iobj_son_tokens = get_son_tokens(sentence,iobj_)
                #cases = [x for x in iobj_son_tokens]
                #result = [Relation(token = x['form'],lemma = x['lemma'],deprel = x['deprel'],upos = x['upos'], metadata = x['feats']) for x in cases]
                result_dic[iobj_['upos']] = Relation(sentence,iobj_)
            return result_dic
    else:
        if 'obj' not in son_tokens_deprel:
            return None
        else:
            objs = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'obj']
            for obj_ in objs:
                #obj_son_tokens = get_son_tokens(sentence,obj_)
                #cases = [x for x in obj_son_tokens]
                #result = [Relation(token = x['form'],lemma = x['lemma'],deprel = x['deprel'],upos = x['upos'], metadata = x['feats']) for x in cases]
                result_dic[obj_['upos']] = Relation(sentence,iobj_)
            return result_dic        
        
def get_ccomp(sentence,token):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if 'ccomp' not in son_tokens_deprel:
        return None
    else:
        ccomps = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'ccomp']
        for ccomp in ccomps:
            ccomp_son_tokens = get_son_tokens(sentence,ccomp)
            ccomp_son_tokens_deprel = [x['deprel'] for x in ccomp_son_tokens]
            if 'mark' not in ccomp_son_tokens_deprel:
                return 'There is no mark son of ccomp'
            else:
                marks = [x for x,y in zip(ccomp_son_tokens,ccomp_son_tokens_deprel) if y == 'mark']
                result = [Relation(token = x['form'], lemma = x['lemma'], deprel = x['deprel'], upos = x['upos'], metadata = x['feats']) for x in marks]
                result_dic[ccomp['upos']] = result
        return result_dic
    
    
def get_xcomp(sentence,token):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if 'xcomp' not in son_tokens_deprel:
        return None
    else:
        xcomps = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'xcomp']
        for xcomp in xcomps:
            result_dic[xcomp['upos']] = {'atributes':Relation(token = xcomp['form'],lemma = xcomp['lemma'],deprel = xcomp['deprel'],upos = xcomp['upos'], metadata = xcomp['feats']),
                                         'conjunctions':None}
            xcomp_son_tokens = get_son_tokens(sentence,xcomp)
            xcomp_son_tokens_deprel = [x['upos'] for x in xcomp_son_tokens]
            if 'mark' not in xcomp_son_tokens:
                continue
            else:
                marks = [x for x,y in zip(xcomp_son_tokens,xcomp_son_tokens_deprel) if y == 'mark']
                result = [Relation(token = x['form'], lemma = x['lemma'], deprel = x['deprel'], upos = x['upos'], metadata = x['feats']) for x in marks]
                resukt_dic[xcomp['upos']]['conjunctions'] = result
        return result_dic
    
    
def get_csubj(sentence,token):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if 'csubj' not in son_tokens_deprel:
        return None
    else:
        csubjs = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'csubj']
        for csubj in csubjs:
            result_dic[csubj['upos']] = {'atributes':Relation(token = csubj['form'],lemma = csubj['lemma'],deprel = csubj['deprel'],upos = csubj['upos'], metadata = csubj['feats']),
                                         'conjunctions':None}
            csubj_son_tokens = get_son_tokens(sentence,csubj)
            csubj_son_tokens_deprel = [x['upos'] for x in csubj_son_tokens]
            if 'mark' not in csubj_son_tokens:
                continue
            else:
                marks = [x for x,y in zip(csubj_son_tokens,csubj_son_tokens_deprel) if y == 'mark']
                result = [Relation(token = x['form'], lemma = x['lemma'], deprel = x['deprel'], upos = x['upos'], metadata = x['feats']) for x in marks]
                resukt_dic[xcomp['upos']]['conjunctions'] = result
        return result_dic
                
def get_expl(sentence,token):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]
    result_dic = {}
    if 'expl' not in son_tokens_deprel:
        return None
    else:
        expls = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'expl']
        for expl in expls:
            result_dic[expl['upos']] = Relation(token = expl['form'], lemma = expl['lemma'], deprel = expl['deprel'], upos = expl['upos'], metadata = expl['feats'])
        return result_dic
    

def get_nsubj(sentence,token):
    son_tokens = get_son_tokens(sentence,token)
    son_tokens_deprel = [x['deprel'] for x in son_tokens]    
    result_dic = {}
    if 'nsubj' not in son_tokens_deprel:
        return None
    else:
        nsubjs = [x for x,y in zip(son_tokens,son_tokens_deprel) if y == 'nsubj']
        for nsubj in nsubjs:
            result_dic[nsubj['upos']] = Relation(token = nsubj['form'],lemma=nsubj['lemma'],deprel = nsubj['deprel'], upos = nsubj['upos'], metadata = nsubj['feats'])
        return result_dic
    
    
   

def get_valence(sentence,token):
    obj = get_deprel(sentence,token,'obj')
    iobj = get_deprel(sentence,token,'iobj')
    ccomp = get_deprel(sentence,token,'ccomp')
    xcomp = get_deprel(sentence,token,'xcomp')
    expl = get_deprel(sentence,token,'expl')
    nsubj = get_deprel(sentence,token,'nsubj')
    csubj = get_deprel(sentence,token,'csubj')
    aux_pass = get_deprel(sentence,token,'aux:pass')
    nsubj_pass = get_deprel(sentence,token,'nsubj:pass')
    if obj is None and iobj is None and ccomp is None and xcomp is None and expl is None:
        return None
    return Valence(token = token['form'], 
                   lemma=token['lemma'],
                   metadata=token['feats'], 
                   xcomp=xcomp,
                   ccomp=ccomp,
                   obj=obj,
                   iobj=iobj,
                   expl=expl,
                   nsubj = nsubj,
                   csubj=csubj,
                   nsubj_pass = nsubj_pass,
                   aux_pass = aux_pass,
                   example=sentence.metadata['text'],
                   rel_set = get_rel_set(sentence,token))
            
            
def main():
    verbs = {}
    with open("pt_bosque-ud-train.conllu") as arq:
        bosque = parse(arq.read())
    for sentence in bosque:
        for verb_index in get_verbs_index(sentence):
            verb_lemma = sentence[verb_index]['lemma']
            if verb_lemma not in verbs.keys():
                verbs[verb_lemma] = Verb(lemma=verb_lemma,valences = [])
            valence = get_valence(sentence,sentence[verb_index])
            if valence is None:
                continue
            else:
                verbs[verb_lemma].add_valence(valence)
        print(f'Done {(bosque.index(sentence)+1)*100/len(bosque):.3f}',end='\r')
    print("Done first part...")
    joblib.dump(verbs,'verbs_dict.joblib')
    d = verbs
    g = {}
    i=0
    for verb in d.keys():
        for valence in d[verb].valences:
            if str(valence) not in g.keys():
                g[str(valence)] = []
            if d[verb] not in g[str(valence)]:
                g[str(valence)].append(d[verb])
        i+=1
        print(f'Done {100*i/len(d.keys()):.2f}',end='\r')
    joblib.dump(g,'valences_dict.joblib')
    print('Done second part...')


if __name__ == "__main__":
    main()
