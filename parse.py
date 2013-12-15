#! /usr/bin/env python
# -*- coding: utf-8 -*-

import re, string
from itertools import izip
import json
import sys


def parse_text():
    text = open('vefx_orig.txt', 'r').read()
    #  correct text errors
    text_edited = text.replace('?ნ', '?')
    text_edited = text_edited.replace('!ნ', '!')
    # remove additional lines

    def rm_sparelines(matched):
        s = '<strophe>\n' + ''.join([matched.group(i) + '\n'
            for i in range(1, 5)]) + r'</strophe>' + '\n'
        return s

    text_edited = re.sub(r'\n(.+)\n\n(.+)\n\n(.+)\n\n(.+)\n\n',
            rm_sparelines, text_edited)
    open('vefx_parsed.txt', 'w').write(text_edited)


def vowel_count(s):
    return sum(c in u'აეიოუ' for c in s)


def strip_word(word):
    excl = set(string.punctuation)
    ret = ''.join(ch for ch in word if ch not in excl)
    return ret.strip()


def build_words_chain(text):
    """ returns a json of the following format

       [ {vowelCount1 : [{ word1 : ['prword1',  ..], ..]} ..} ]

    """
    strophe_xs = re.findall(r'<strophe>\n(.+\n.+\n.+\n.+)\n</strophe>', text)

    wordschain = {}

    for strophe in strophe_xs:
        lines = strophe.split('\n')
        last_words = []

        for line in lines:
            words = map(strip_word, line.split(' '))
            for prword, word in izip(words, words[1:]):
                word_vwc = vowel_count(word)
                if word_vwc not in wordschain:
                    wordschain[word_vwc] = []
                for word_obj in wordschain[word_vwc]:
                    if word_obj[u'aWord'] == word:
                        break
                else:
                    word_obj = {'aWord': word, 'previousWords': [], 'rhymes':[]}
                    wordschain[word_vwc].append(word_obj)
                if prword not in word_obj['previousWords']:
                    word_obj['previousWords'].append(prword)
                if word == words[-1]:
                    last_words.append(word_obj)

        for rhyme1_obj in last_words:
            for rhyme2_obj in last_words:
                if not rhyme1_obj is rhyme2_obj:
                    rhyme2_word = rhyme2_obj['aWord']
                    if rhyme2_word not in rhyme1_obj['rhymes']:
                        rhyme1_obj['rhymes'].append(rhyme2_word)

    # this is needed because something is wrong with a text,
    # should be removed later
    del wordschain[0]

    #print json.loads(json.dumps(wordschain,ensure_ascii=False))
    f = open('wordschain.json', 'w')
    f.write(json.dumps(wordschain,indent=4, 
        ensure_ascii=False).encode('utf-8'))
    f.close()


def main():
    #parse_text()
    text = open('vefx_parsed.txt', 'r').read()
    text = text.decode('utf-8')
    build_words_chain(text)


if __name__ == '__main__':
    main()
