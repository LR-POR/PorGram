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
    whereas 'trabalhadeira' is a irregular feminine form of latter lemma.
    TODO: include regular and irregular diminutives"""
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
	for lemma in entries.keys():
		for form in entries[lemma]:
			if form.endswith("inhas"):
				print_irreg_form(form[:-1],lemma,"FEM-SUFFIX")
			else:
				print_irreg_form(form,lemma,"A-PL-SUFFIX")
		
		
def classify_adjs(lemma_dict):
    """Classify adjectives into the types defined in the grammar in the lexicon tdl files.
    Adjective forms are also classified into regular and irregular forms according to whether
    they follow gender and number inflectional rules."""
    infl=[]
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
        for form, feats in lemma_dict[lemma,pos]:
            if feats == ['SG']:
                ident=format_lemma(i,lemma)
                i+=1
                unif.append(ident)
            elif feats == []:
                ident=format_lemma(i,lemma)
                i+=1
                infl.append(ident)
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
    dic["infl"]=infl
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
		'infl': 'infl-form',
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
            if k == "unif" or k == "infl":
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







    

