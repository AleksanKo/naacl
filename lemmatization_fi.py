import re
import requests
import stanza

from collections import Counter
from string import punctuation

stanza.download("fi")

nlp = stanza.Pipeline('fi')

with open("aukio.txt", "r",encoding='latin-1') as f:
    text = f.read()

paragraphs = text.split("\n\n")
paragraphs = [i.replace("\n", " ") for i in paragraphs]

def lower_upper(word):
    if word.isupper():
        word = word.capitalize()
    else:
        pass
    return word

#preprocessing
#remove luku: [A-Za-z] luku
text = re.sub('[IMLCXV]+\s','', text)

text = text.replace("\n", " ")
text = ' '.join(text.split())
text = text.replace("“", " ")
text = text.replace("”", " ")
text = text.replace("\"", " ")
text = text.replace("'", " ")
text = text.replace("‑", " ")
text = text.replace("_", " ")
text = ' '.join([lower_upper(word) for word in text.split()])

punct = punctuation + ' '

pers_ent = []
lemm_names = []
lemm_names_filtered = []
names_filtered = []

for paragraph in paragraphs:
    doc = nlp(paragraph)

    words = {word.text : word.lemma for sent in doc.sentences for word in sent.words}

    for ent in doc.entities:
        if ent.type == "PER":
            pers_ent.append(ent.text)

    counter = Counter(pers_ent)

    pers_ent_filtered = [text for text in counter.keys() if counter[text] >=2]

    print(len(pers_ent_filtered), "len pers_ent_filtered")

    #lemmatizing names

    for per in pers_ent_filtered:
        name = per.split()
        p = ''
        person = ''
        for n in name:
            try:
                p = words[n]
                if len(name) > 1:
                    person += p + ' '
                else:
                    person = p
            except KeyError:
                person = p

        lemm_names.append(person)

    lemm_names = list(set(lemm_names))
    print(len(lemm_names), "len lemm_names")

    #filtering lemmatized names

    for name in lemm_names:
        if name.lower() != name:
            lemm_names_filtered.append(name.split("#")[0].strip())

    #filtering names that are present as tokens
    for i in lemm_names_filtered:
        for j in punct:
            name = j + i + j
            if name in text:
                names_filtered.append(i)

    names_filtered = list(set(names_filtered))
    print(sorted(names_filtered), "names_filtered")


characters = names_filtered[::]
characters.sort()
with open("results_draft.txt", "w+") as f:
  print("Draft results", "\n", characters, file=f)


# method 1: searching for the shortest name
method_1 = []
k = []
l = characters[::]

j = 0
i = 0
while True:
    try:
    # the duplicate is essentially a word form that differs only in ending
        if l[j+1].startswith(l[i]) and len(l[j+1])-len(l[i]) <= 4:
        # adding true value to list and checking that it's not already here
            if l[i] not in method_1:
                method_1.append(l[i])
                print(method_1)
            # adding duplicate to blacklist
            k.append(l[j+1])
            j+=1
        else:
            # checking that value not in blacklist and not already in the list
            if l[i] not in k and l[i] not in method_1:
                method_1.append(l[i])
                print(method_1)
            j+=1
            i = j
    except:
        break

with open("results.txt", "a") as f:
    print("Results for method 1", "\n", method_1, file=f)
print(set(characters) - set(method_1))

#method 2: searching in Wikipedia/Wiktionary

method_2 = []
for i in characters:
    if requests.get('https://en.wikipedia.org/wiki/' + i.split()[-1]).status_code != 404:
        method_2.append(i)

method_2_wikt = []
for i in characters:
    if requests.get('https://en.wiktionary.org/wiki/' + i.split()[-1]).status_code != 404:
        method_2_wikt.append(i)

method_2.sort()
method_2_wikt.sort()

with open("results.txt", "a") as f:
    print("Results for method 2, Wikipedia", "\n", method_2, file=f)
#print(set(characters) - set(method_2)

with open("results.txt", "a") as f:
    print("Results for method 2, Wiktionary", "\n", method_2_wikt, file=f)
#print(set(characters) - set(method_2_wikt))

# 3rd method: trimming suffixes
suffixes = ('a','n','ia','iä')
method_3 = []
for i in characters:
    if not i.endswith(suffixes):
        method_3.append(i)

with open("results_kolea_talo.txt", "a") as f:
    print("Results for method 3", "\n", method_3, file=f)
#print(set(characters) - set(method_3))
