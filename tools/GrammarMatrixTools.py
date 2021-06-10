#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

@author: leonel
"""

import re
import sys
sys.path.append("/home/leonel/MorphoBr/src")
from SimplifyEntries import extract_entries,build_entry_dict_list,build_lemma_dict 

"pairs from fem-suff rule in my-irules.tdl"
MAPPING={'éu': 'oa', 'eu': 'eia', 'ão': 'ona', 'ês': 'esa', 'or': 'ora', '[rn]u': '[rn]ua', '[^ã]o': '[^ã]a'}

def extract_lines(infile):
    with open(infile) as f:
        return [line.strip() for line in f.readlines()]


def extract_words(lines):
    """Extract (orth,pos) pairs from grammar choices file specified with the Grammar Matrix questionnaire.
    """
    words=[]
    for line in lines:
        if "orth" in line and not "lri" in line and not "sentence" in line:
            word=line.split("=")[1]
            cat=re.split(r"\d+",line)[0]
            words.append((word,cat))
    return words

def build_sections_dict(lines):
    """Build dictionary str -> list, where str is the name of a section and list contains the lines of the section.
    """
    sections={}
    for line in lines:
        if re.match(r"section=",line):
            name=line.split("=")[1]
            sections[name]=[]
        else:
            if line.strip() != "":
                sections[name].append(line)
    return sections

def build_sents_dict(sents):
    """Build dictionary str -> list, where str is a sentence identifier and list contains the values for
    the orth attribute and the star attribute of the sentence (if there is one) in form of tuples (attribute, value).
    """
    dic={}
    for sent in sents:
        num,att,val=re.split(r"_|=",sent)
        if dic.get(num):
            dic[num].append((att,val))
        else:
            dic[num]=[(att,val)]
    return dic

def extract_ungrammatical_sents(dic):
	ungram=[]
	for sent in dic.keys():
		val=dic.get(sent)
		if len(val) == 2:
			ungram.append(val[0][1])
	return ungram

def extract_grammatical_sents(dic):
	gram=[]
	for sent in dic.keys():
		val=dic.get(sent)
		if len(val) == 1:
			gram.append(val[0][1])
	return gram

def freq_dist(sents):
    """Create frequency distribution of the words in a test file."""
	freqs={}
	for sent in sents:
		words=re.split(r"\s+",sent)
		for word in words:
			if freqs.get(word):
				freqs[word]+=1
			else:
				freqs[word]=1
	return freqs


def build_irules_dict(infile):
    """Transform irules.tdl file in a dictionary."""
	lines=extract_lines(infile)
	rules={}
	i=0
	c=len(lines)
	while(i<c):
		if ":=" in lines[i]:
			name=lines[i].split(":=")[0].strip()
			rules[name]=[lines[i+1],lines[i+2]]
		i+=1
	return rules

def compare_rules(irules1,irules2):
    """Compare rule definitions in two different irules.tdl files.
    This is is useful to keep track of changes made manually and with the Grammar Matrix."""
	rules1=set(build_irules_dict(irules1).keys())
	rules2=set(build_irules_dict(irules2).keys())
	r1_diff_r2=rules1.difference(rules2)
	r2_diff_r1=rules2.difference(rules1)
	if r1_diff_r2:
		print("not found in",irules2,r1_diff_r2)
	elif r2_diff_r1:
		print("not found in",irules1,r2_diff_r1)
	else:
		print("files have the same inflectional rule types")
		
def print_freq(freqs):
	keys=list(freqs.keys())
	keys.sort()
	for key in keys:
		print(key,freqs[key])


def pprint(words):
    words.sort()
    for word in words:
        print(word[0],word[1])

def morphobr(infile="/home/leonel/MorphoBr/adjectives/new-adjectives.dict"):
    """Create dictionary (lemma,pos) -> list with (form,feats), where feats is the list of features of form."""
    entries=extract_entries(infile)
    entry_dict_list=build_entry_dict_list(entries)
    return build_lemma_dict(entry_dict_list)


def get(suff,mapping):
    for k in mapping.keys():
        if re.match(k,suff):
            return mapping[k]
    return None

def is_regular(lemma,feminine, mapping=MAPPING):
    """Check whether a form of a lemma is regular according to the given mapping of suffixal changes,
    e.g. 'francesa' and 'trabalhadora' are regular feminine forms of 'francês' and 'trabalhador',
    whereas 'trabalhadeira' is a irregular feminine form of latter lemma."""
    suff1=lemma[-2:]
    suff2=get(suff1,mapping)
    if suff2 and re.match(f'.*{suff2}$',feminine):
        return True
    else:
        return False

def format_lemma(counter,lemma):
    if counter == 0:
        return lemma
    else:
        return f"{lemma}_{str(counter)}"
    

def is_reg_dim_pl(lemma,form):
    """Check whether a form of a lemma is a regular plural form."""
    ending=form[-2:]
    boolean=f"{lemma}zinh{ending}" == form or f"{lemma}inh{ending}" == form or f"{lemma[:-1]}inh{ending}" == form
    return boolean

def irreg_pl_dict(lemma,form,feats,plurals):
    "TODO: check if all forms are classified"
    if feats == ['M','PL'] and lemma.endswith("ão"):
        if not plurals.get(lemma):
            plurals[lemma]={'reg':[],'irreg':[]}
        if form.endswith("ões"):
            plurals[lemma]['reg'].append(form)	
        else:
            plurals[lemma]['irreg'].append(form)
    elif len(feats) > 2 and feats[-3:] == ['DIM','M','PL'] and re.match(r".+[ãõ][oe]zinhos",form):
        if not plurals.get(lemma):
            plurals[lemma]={'reg':[],'irreg':[]}
        if form.endswith("õezinhos"):
            plurals[lemma]['reg'].append(form)	
        elif form.endswith("ãozinhos") or form.endswith("ãezinhos"):
            plurals[lemma]['irreg'].append(form)
    elif 'DIM' in feats and feats[-1] == 'PL' and re.match(r".+z?inh[oa]s",form):
        if not plurals.get(lemma):
            plurals[lemma]={'reg':[],'irreg':[]}
        if is_reg_dim_pl(lemma,form):
            plurals[lemma]['reg'].append(form)
        else:
            plurals[lemma]['irreg'].append(form)

            
def update_dict(key,value,dic):
    if dic.get(key):
        dic[key].append(value)
    else:
        dic[key]=[value]

def lemma_diminutive(form):
    patterns=[r"(.+z)ezinh[ao]s$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}inho"
        
    patterns=[r"(.+)eiazinhas$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}euzinho"
        
    patterns=[r"(.+[^e])iazinhas$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}euzinho"
        
    patterns=[r"(.+)([eauo])izinh[oa]s$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}{m.groups()[1]}lzinho"

    patterns=[r"(.+)([oa]r)[ea](zinh)[oa]s$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}{m.groups()[1]}zinho"

    patterns=[r"(.+)es[ea](zinh)[oa]s$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}esinho"

    patterns=[r"(.+)([ãõ][eo]{0,1}|oa)(zinh[oa])(s)$",
		  r"(.+)o(az)?inhas$",
		  r"(.+)on(az)?inhas$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}ãozinho"

    patterns=[r"(.+[^u])a(zinh)as$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}o{m.groups()[1]}o"

    patterns=[r"(.+u)a(zinh)as$",
		  r"(.+)a(zinh)as$"]
    for pat in patterns:
        m=re.match(pat,form)
        if m:
            return f"{m.groups()[0]}{m.groups()[1]}o"
    if re.match(r"(.+)inh[oa]s",form):
        return form



def build_plural_irregs(plurals):
    entries={}
    for lemma in plurals.keys():
        irreg=plurals[lemma]['irreg']
        reg=plurals[lemma]['reg']
        if irreg and reg:
            for form in reg:
                lem_dim=lemma_diminutive(form)
                if lem_dim:
                    if lem_dim != form:
                        update_dict(lem_dim,form,entries)
                else:
                    update_dict(lemma,form,entries)
        if irreg:
            for form in irreg:
                lem_dim=lemma_diminutive(form)
                if lem_dim:
                    if lem_dim != form:
                        update_dict(lem_dim,form,entries)
                else:
                    update_dict(lemma,form,entries)
    return entries

def print_irreg_form(form,lemma,affix):
    """Print entry of irregs.tab file encoding an exception to a regular inflectional rule."""
    print(f"{form} {affix} {lemma}")
    
def print_plural_irregs(entries):
    affix="A-PL-SUFFIX"
    for lemma in entries.keys():
        for form in entries[lemma]:
            print_irreg_form(form,lemma,affix)
		
def classify_adjs(lemma_dict):
    """Classify adjectives into the types defined in the grammar in the lexicon tdl files.
    Adjective forms are also classified into regular and irregular forms according to whether
    they follow gender and number inflectional rules."""
    unif=[]
    non_reg=[]
    reg=[]
    superl=[]
    dim=[]
    aug=[]
    dim_aug=[]
    dic={}
    fem_forms={}
    plurals={}
    for lemma,pos in lemma_dict.keys():
        plurals[lemma]={'reg':[],'irreg':[]}
        i=0
        fems=[]
        for form, feats in lemma_dict[lemma,pos]: # TODO: include 'simples'
            if feats == ['SG']:
                ident=format_lemma(i,lemma)
                i+=1
                unif.append(ident)
            elif feats == ['SUPER','M','SG']:
                superl.append((lemma,form))
            elif feats == ['DIM','M','SG']:
                dim.append((lemma,form))
            elif feats == ['AUG','M','SG']:
                aug.append((lemma,form))
            elif feats == ['AUG','DIM','M','SG']:
                dim_aug.append((lemma,form))
            elif feats == ['F','SG']:
                fems.append(form)
            else:
                irreg_pl_dict(lemma,form,feats,plurals) 
        for fem in fems:
            if is_regular(lemma,fem):
                ident=format_lemma(i,lemma)
                i+=1
                reg.append((ident,fem))
                fem_forms[lemma]=fem		
            else:
                ident=format_lemma(i,lemma)
                i+=1
                non_reg.append((ident,fem))
    dic["unif"]=unif
    dic["non_reg"]=non_reg
    dic["reg"]=reg
    dic["dim"]=dim
    dic["superl"]=superl
    dic["aug"]=aug
    dic["dim_aug"]=dim_aug
    return dic, fem_forms, plurals


def print_tdl_entry(ident,form,lemma,a_type):
    adj=f"""{ident} := {a_type}-adj-lex &
		    [ STEM < "{form}" >,
		    SYNSEM.LKEYS.KEYREL.PRED "_{lemma}_a_rel" ].\n"""
    print(adj)

def print_tdl(dic,fem_forms,plurals):
    a_types={'unif': 'uniform',
             'reg': 'non-uniform',
             'non_reg': 'non-uniform',
             'dim': 'dim',
             'superl' : 'abs',
             'aug': 'aug',
             'dim_aug': 'dim-aug'}
    irreg_fem_forms=[]
    for k in dic.keys():
        entry=[]
        for e in dic[k]:
            if k == "unif":
                lemma=e.split("_")[0]
                ident=e
                a_type=a_types[k]
                print_tdl_entry(ident,lemma,lemma,a_type)
            elif k == "reg":
                ident=e[0]
                lemma=ident.split("_")[0]
                a_type=a_types[k]
                print_tdl_entry(ident,lemma,lemma,a_type)
            elif k == "non_reg":
                ident=e[0]
                lemma=ident.split("_")[0]
                form=e[1]
                is_regular=lemma in [lemma.split("_")[0] for lemma,form in dic["reg"]]
                if is_regular:
                    fem=fem_forms.get(lemma)
                    irreg_fem_forms.append((fem,lemma))
                else:
                    if lemma not in entry:
                        entry.append(lemma)
                        a_type=a_types[k]
                        print_tdl_entry(ident,lemma,lemma,a_type)
                irreg_fem_forms.append((form,lemma))
            else:
                if k in ["dim","aug","dim_aug","superl"]:
                    lemma=e[0].split("_")[0]
                    form=e[1]
                    ident=form
                    print_tdl_entry(ident,form,lemma,a_types[k])
    
    print_plural_irregs(build_plural_irregs(plurals))
    for form,lemma in irreg_fem_forms:
        print_irreg_form(form,lemma,"FEM-SUFFIX")

def main(infile):
    lemma_dict=morphobr(infile)
    dic,fems,plurals=classify_adjs(lemma_dict)
    print_tdl(dic,fems,plurals)
    
if __name__ == "__main__":
    main(sys.argv[1])







    

