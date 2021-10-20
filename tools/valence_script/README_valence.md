# How to run the code

First you must have two libraries: joblib and conllu, so ou must get them

``` pip install conllu joblib```

Then you can work with the data in the following form:

```from valences import *
import joblib
val = joblib.load('valences_dict.joblib')
```

*valences_dict.joblib* is a python dictionary, and its keys what I call valences, which basically are some pattern of deprels that a (set of) verbs satisfy. If you type

Typing

```list(val.keys())[:5]
['<VERB,expl>', '<nsubj,VERB,obj>', '<VERB,obj>', '<nsubj,expl,VERB>', '<expl,VERB>']
```

So, for instance, the key '<nsubj,VERB,obj>' means every VERB that has only nsubj and obj as sons and the order in the sentence is nsubj -- verb -- obj.

Typing

```
val['<nsubj,VERB,obj>'][:20]
```

The output is

```
[situar, continuar, manter, esperar, deixar, ser, correr, querer, fugir, ir, encontrar, gastar, juntar, reivindicar, faltar, lembrar, considerar, especializar, dispor, encomendar]
```

So these are the first 20 verbs that appears in the corpus in the form nsubj -- verb -- obj

Looking at the first verb, situar,

```
val['<nsubj,VERB,obj>'][0]
```

The output is

```
situar
```

This is an object called Verb and it has one important attribute and one important method. The attribute is *valences*. It shows a list with every setting of relations it appears in the corpus

```
val['<nsubj,VERB,obj>'][0].valences
```

The output is

```[<VERB,expl>, <nsubj,VERB,obj>, <VERB,obj>, <nsubj,expl,VERB>, <nsubj,expl,VERB>, <expl,VERB>, <nsubj,expl,VERB>, <expl,VERB>, <VERB,expl>, <nsubj,VERB,expl>, <VERB,expl>, <expl,VERB>]
```

The method is print. This shows every setting of this verb in the corpus


Typing

```
print(val['<nsubj,VERB,obj>'][0].print())
```

The output is

```
situar+Mood:Sub+Number:Sing+Person:3+Tense:Pres+VerbForm:Fin nsubj PRON+se+Acc+Fem+Sing+3+Prs
situar+VerbForm:Inf PRON+se+Acc+Fem+Sing+3+Prs
situar+VerbForm:Ger PRON+se+Acc+Fem+Sing+3+Prs
situar+Mood:Ind+Number:Sing+Person:3+Tense:Pres+VerbForm:Fin nsubj PRON+se+Acc+Fem+Sing+3+Prs
situar+Mood:Ind+Number:Sing+Person:3+Tense:Pres+VerbForm:Fin obj nsubj 
situar+VerbForm:Inf PRON+se+Acc+Masc+Sing+3+Prs
situar+VerbForm:Inf PRON+se+Acc+Masc+Plur+3+Prs
situar+VerbForm:Ger obj 
situar+VerbForm:Inf nsubj PRON+se+Acc+Fem+Sing+3+Prs
```

You can also access a specific setting in the verb, returning to

```
val['<nsubj,VERB,obj>'][0].valences[1]
```

The output is

```
<nsubj,VERB,obj>
```

Which is another object. Its methods are the deprels shown in its printed form. So, in this case, we can access 

```
val['<nsubj,VERB,obj>'][0].valences[1].nsubj
```

And the output is

```
{'PRON': [que,nsubj,PRON]}
```

A dictionary with the every nsubj son of the verb. In this case we have only one. We can access this by accessing a regular dictionary. The visualization is very self contained though. The only usefull information not shown in the visualization is the marks and cases, sons of the PRON in this case (if exists). One can access by typing


```
val['<nsubj,VERB,obj>'][0].valences[1].nsubj['PRON'].relation
```

In this case there are no sons of the PRON token with mark or case deprel.

Returing to the valence object, 

```
val['<nsubj,VERB,obj>'][0].valences[1]
```

One can access the sentence by typing

```
val['<nsubj,VERB,obj>'][0].valences[1].example
```

And the output is

```
'Daniel Blaufuks apresenta um trabalho construído a partir de imagens previamente existentes, o que situa este trabalho na linha das mais recentes preocupações do autor (a questão da perda de referência das imagens fotográficas, o trabalho sobre a simulação), não deixando contudo de estar sempre presente o registo poético, em parte autobiográfico, que sempre o caracterizou:'
```



If there are deprels such as nsubj:pass or aux:pass in the valence object, one can access by typing valence.nsubj_pass or valence.aux_pass. 

