#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import fnmatch
import re
from collections import Counter
import wordgraph


punctuations = '“”‘’!()-[]{};:\'\"\\,<>./?@#$^&*_~'

resources_path = os.path.dirname(__file__) + '/resources/'
punct_tag = 'PUNCT'
pos_separator = '/'
pos_tags = ['Np', 'Nc', 'Nu', 'N', 'V', 'A', 'P', 'R', 'L', 'M', 'E', 'C', 'CC', 'I', 'T', 'Y', 'Z', 'X']
overlap_check_tags = ['Np', 'N', 'V']


def text_to_vector(text):
    words = text.split(' ')
    return Counter(words)


def read_text_file(file_path):
    sentences = []
    pos_separator_re = re.escape(pos_separator)
    f_file = open(file_path, encoding='utf8')
    for line in f_file:
        aa = line.strip().replace('\ufeff', '')
        if len(aa) > 0:
            tagged_words = aa.split(' ')
            lst_sentence_tagged_word = []
            for tagged_word in tagged_words:
                # Splitting word, POS
                m = re.match('^(.+)' + pos_separator_re + '(.+)$', tagged_word)
                word, POS = m.group(1), m.group(2)
                if POS not in pos_tags or word in punctuations:
                    POS = punct_tag
                else:
                    lst_sentence_tagged_word.append([word, POS])
            sentences.append(lst_sentence_tagged_word)
    return sentences


def read_stop_word_from_file():
    with open(resources_path + 'Stopwords/stopwords.vi.dat', 'r', encoding='utf8') as f:
        lst_stop_words = [line.strip().replace(' ', '_').replace('\ufeff', '').lower() for line in f]
    return lst_stop_words


def sort_sentence_by_overlap(lst_sentences):
    lst_check_overlap = []
    for i in range(len(lst_sentences)):
        overlap_sentence = ''
        sentence_length = 0
        for tagged_word in lst_sentences[i]:
            word, POS = tagged_word[0], tagged_word[1]
            if POS in overlap_check_tags:
                overlap_sentence += word.lower() + ' '
            if POS != punct_tag:
                sentence_length += 1
        lst_check_overlap.append([i, 0, sentence_length, dict(text_to_vector(overlap_sentence.strip()))])

    for i in range(len(lst_check_overlap)):
        """ Loop over items and unpack each item. """
        for word_base, weight_base in lst_check_overlap[i][3].items():
            if weight_base > 1:
                for j in range(len(lst_check_overlap)):
                    if j != i:
                        if word_base in lst_check_overlap[j][3].keys():
                            if weight_base > lst_check_overlap[j][3][word_base]:
                                lst_check_overlap[i][1] += weight_base / lst_check_overlap[j][3][word_base]
    lst_check_overlap = sorted(lst_check_overlap, key=lambda sentence: (sentence[1], sentence[2]), reverse=True)
    result = []
    for i in range(len(lst_check_overlap)):
        result.append(lst_sentences[lst_check_overlap[i][0]])
    return result


if __name__ == '__main__':
    print('Begin')
    lstStopWords = read_stop_word_from_file()
    path_original = resources_path + 'MSC-VN/original/pos/'
    path_system = resources_path + 'MSC-VN/system/'
    for iCluster in range(1, 116):
        f = str(iCluster).rjust(3, "0")
        # try:
        print("File: ", f)
        lstTaggedSentences = read_text_file(os.path.join(path_original, f))
        lstTaggedSentences = sort_sentence_by_overlap(lstTaggedSentences)

        """ Print source sentences """
        for tmp_tagged_sentence in lstTaggedSentences:
            tmp_plain_sentence = ''
            for tagged_word in tmp_tagged_sentence:
                tmp_plain_sentence += tagged_word[0] + ' '
            tmp_plain_sentence = tmp_plain_sentence.strip()
            print('\t%s' % tmp_plain_sentence)

        """ Frequency """
        compressResult = wordgraph.action(lstTaggedSentences, lstStopWords)
        target_org = open(os.path.join(path_system, f), 'w', encoding='utf8')
        target_org.write(compressResult.replace('_', ' ').strip())
        target_org.close()
        print('==>', compressResult.strip())
        print('-------------------------------------------------------------------------------------')
        # except:
        #     print('except')