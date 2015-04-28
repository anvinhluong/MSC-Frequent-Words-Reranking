#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from collections import Counter
from nltk import pos_tag, word_tokenize
import wordgraph

resources_path = os.path.dirname(__file__) + '/resources/'
punct_tag = 'PUNCT'
pos_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS', 'MD', 'NN',
            'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR', 'RBS', 'RP',
            'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB']
overlap_check_tags = ['NN', 'NNS', 'NNP', 'NNPS', 'VB', 'VBD', 'VBG', 'VBN', 'VBP', 'VBZ']


def text_to_vector(text):
    words = text.split(' ')
    return Counter(words)


def read_text_file(file_name):
    sentences = []
    path = resources_path + 'Fusion_Corpus_AMT/Intersection/'
    file_type = '.src.txt'

    f_file = open(path + '/' + file_name + file_type, encoding='utf8')
    for line in f_file:
        aa = line.strip().replace('\ufeff', '')
        seg = word_tokenize(aa)
        lst_word_pos = pos_tag(seg)
        sentence = []
        for i in range(len(lst_word_pos)):
            if lst_word_pos[i][1] not in pos_tags:
                # sentence.append([lst_word_pos[i][0], punct_tag])
                pass
            else:
                sentence.append([lst_word_pos[i][0], lst_word_pos[i][1]])
        sentences.append(sentence)
    f_file.close()
    return sentences


def read_stop_word_from_file():
    with open(resources_path + 'Stopwords/stopwords.en.dat', 'r', encoding='utf8') as f:
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
    path_original = resources_path + 'Fusion_Corpus_AMT/Intersection/'
    path_system = resources_path + 'Fusion_Corpus_AMT/system/'

    for iCluster in range(1, 301):
        s_cluster = str(iCluster).rjust(3, "0")
        print("File: ", s_cluster)
        lstTaggedSentences = read_text_file(str(iCluster).rjust(3, "0"))
        lstTaggedSentences = sort_sentence_by_overlap(lstTaggedSentences)

        """ Print source sentences """
        for tmp_tagged_sentence in lstTaggedSentences:
            tmp_plain_sentence = ''
            for tagged_word in tmp_tagged_sentence:
                tmp_plain_sentence += tagged_word[0] + ' '
            tmp_plain_sentence = tmp_plain_sentence.strip().replace(" 'm ", "'m ").replace(" 'll ", "'ll ").replace(" 'd ", "'d ").replace(" n't ", "n't ").replace(" 's ", "'s ")
            print('\t%s' % tmp_plain_sentence)

        compressResult = wordgraph.action(lstTaggedSentences, lstStopWords)
        target_org = open(os.path.join(path_system, s_cluster + '.sys.txt'), 'w', encoding='utf8')
        target_org.write(compressResult.strip())
        target_org.close()
        print('==>', compressResult.strip())
        print('-------------------------------------------------------------------------------------')
