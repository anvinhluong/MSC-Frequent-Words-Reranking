#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import Counter

verb_pos_set = ['V']


class SW:
    i_sentence_id = -1
    i_word_id = -1

    def __init__(self, i_sentence_id, i_word_id):
        self.i_sentence_id = i_sentence_id
        self.i_word_id = i_word_id


class NODE:
    i_node_id = -1
    s_text = ''
    s_pos_tag = ''
    sentence_id = []
    heads = []
    tails = []
    puncts = set()
    syn_text = set()

    def __init__(self, word):
        self.i_node_id = -1
        self.s_text = word[0]
        self.s_pos_tag = word[1]
        self.sentence_id = []
        self.heads = []
        self.tails = []
        self.puncts = set()
        self.syn_text = set()

    def set_text(self, new_text):
        if self.s_text != '':
            self.s_text = new_text
        self.syn_text.add(new_text)

    def get_text(self):
        return self.s_text

    def append_head(self, new_head_node):
        self.heads.append(new_head_node)

    def append_tail(self, new_tail_node):
        self.tails.append(new_tail_node)


def add_sentence_to_graph(i_sentence_id, lst_word_pos, lst_node, i_general_node_id, s_node, e_node, lst_stop_words):
    lst_recent_inserted_node = []
    s_node.sentence_id.append(SW(i_sentence_id, -1))
    pre_node = s_node
    tmp_node = NODE(['', ''])
    i = 0
    for w in lst_word_pos:
        """ Find candidate Nodes """
        lst_candidate = []
        for word_node in lst_node:
            if word_node.s_pos_tag == w[1]:
                if word_node.get_text().lower() == w[0].lower():
                    b_check_candidate_in_recent_inserted_node = 0
                    for recent_node in lst_recent_inserted_node:
                        if recent_node.i_node_id == word_node.i_node_id:
                            b_check_candidate_in_recent_inserted_node = 1
                            break
                    if b_check_candidate_in_recent_inserted_node == 0:  # Candidate not in recent Nodes
                        k = [None] * 6000
                        tmp_unique_set = set()
                        reversed_path_node = []
                        get_all_path_between_2_nodes(len(lst_node), word_node, k, tmp_unique_set, 0, reversed_path_node, pre_node.i_node_id)
                        if len(reversed_path_node) == 0:
                            lst_candidate.append(word_node)

        if w[0].lower() in lst_stop_words:
            if len(lst_candidate) > 0:
                """ Right context """
                try:
                    if i == (len(lst_word_pos) - 1):
                        s_right_word = 'n-end'
                    else:
                        s_right_word = lst_word_pos[i + 1][0].lower()
                except:
                    s_right_word = ''

                lst_right_candidate = []
                for candidate in lst_candidate:
                    b_check_right_context = 0
                    for right_candidate in candidate.tails:
                        if right_candidate.get_text().lower() == s_right_word:
                            b_check_right_context += 1
                    if b_check_right_context > 0:
                        lst_right_candidate.append(candidate)
                lst_candidate = lst_right_candidate

        if len(lst_candidate) == 0:
            """ Insert new Node """
            tmp_node = NODE(w)
            tmp_node.i_node_id = i_general_node_id[0]
            i_general_node_id[0] += 1
            tmp_node.sentence_id.append(SW(i_sentence_id, i))
            tmp_node.append_head(pre_node)
            lst_node.append(tmp_node)
            lst_recent_inserted_node.append(tmp_node)
            pre_node.append_tail(tmp_node)
            pre_node = tmp_node
        elif len(lst_candidate) == 1:
            tmp_node = lst_candidate[0]
            tmp_node.sentence_id.append(SW(i_sentence_id, i))
            tmp_node.append_head(pre_node)
            lst_recent_inserted_node.append(tmp_node)
            pre_node.append_tail(tmp_node)
            pre_node = tmp_node
        else:
            """ Check candidate in tails/sub-tails of recent node """
            i_min_distance = 999999999
            for i_can_node in range(len(lst_candidate)):
                k = [None] * 6000
                tmp_unique_set = set()
                available_path_node = []
                get_all_path_between_2_nodes(len(lst_node), pre_node, k, tmp_unique_set, 0, available_path_node, lst_candidate[i_can_node].i_node_id)

                if len(available_path_node) == 0:
                    lst_candidate[i_can_node] = [999999999, lst_candidate[i_can_node]]
                else:
                    available_path_node = sorted(available_path_node, key=lambda path: len(path))
                    lst_candidate[i_can_node] = [len(available_path_node[0]), lst_candidate[i_can_node]]
                    if len(available_path_node[0]) < i_min_distance:
                        i_min_distance = len(available_path_node[0])

            tmp_lst_candidate = []
            for i_can_node in range(len(lst_candidate)):
                if lst_candidate[i_can_node][0] == i_min_distance:
                    tmp_lst_candidate.append(lst_candidate[i_can_node][1])
                lst_candidate[i_can_node] = lst_candidate[i_can_node][1]
            if len(tmp_lst_candidate) > 0:
                lst_candidate = tmp_lst_candidate

            """ Check left-right context """
            """ Left context """
            try:
                if i == 0:
                    s_left_word = 'n-start'
                else:
                    s_left_word = lst_word_pos[i - 1][0].lower()
            except:
                s_left_word = ''

            lst_left_candidate = []
            for candidate in lst_candidate:
                b_check_left_context = 0
                for left_candidate in candidate.heads:
                    if left_candidate.get_text().lower() == s_left_word:
                        b_check_left_context += 1
                if b_check_left_context > 0:
                    lst_left_candidate.append(candidate)

            if len(lst_left_candidate) == 0:
                """ Right context """
                try:
                    if i == (len(lst_word_pos) - 1):
                        s_right_word = 'n-end'
                    else:
                        s_right_word = lst_word_pos[i + 1][0].lower()
                except:
                    s_right_word = ''

                lst_right_candidate = []
                for candidate in lst_candidate:
                    b_check_right_context = 0
                    for right_candidate in candidate.tails:
                        if right_candidate.get_text().lower() == s_right_word:
                            b_check_right_context += 1
                    if b_check_right_context > 0:
                        lst_right_candidate.append(candidate)

                if len(lst_right_candidate) == 0:
                    """ Higher frequency """
                    max_frequency = len(lst_candidate[0].sentence_id)
                    candidate_max_frequency = lst_candidate[0]
                    for candidate in lst_candidate:
                        if len(candidate.sentence_id) > max_frequency:
                            max_frequency = len(candidate.sentence_id)
                            candidate_max_frequency = candidate

                    tmp_node = candidate_max_frequency
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
                elif len(lst_right_candidate) == 1:
                    tmp_node = lst_right_candidate[0]
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
                else:
                    """ Higher frequency """
                    max_frequency = len(lst_right_candidate[0].sentence_id)
                    candidate_max_frequency = lst_right_candidate[0]
                    for candidate in lst_right_candidate:
                        if len(candidate.sentence_id) > max_frequency:
                            max_frequency = len(candidate.sentence_id)
                            candidate_max_frequency = candidate

                    tmp_node = candidate_max_frequency
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
            elif len(lst_left_candidate) == 1:
                tmp_node = lst_left_candidate[0]
                tmp_node.sentence_id.append(SW(i_sentence_id, i))
                tmp_node.append_head(pre_node)
                lst_recent_inserted_node.append(tmp_node)
                pre_node.append_tail(tmp_node)
                pre_node = tmp_node
            else:
                """ Right context """
                try:
                    if i == (len(lst_word_pos) - 1):
                        s_right_word = 'n-end'
                    else:
                        s_right_word = lst_word_pos[i + 1][0].lower()
                except:
                    s_right_word = ''

                lst_right_candidate = []
                for candidate in lst_left_candidate:
                    b_check_right_context = 0
                    for right_candidate in candidate.tails:
                        if right_candidate.get_text().lower() == s_right_word:
                            b_check_right_context += 1
                    if b_check_right_context > 0:
                        lst_right_candidate.append(candidate)

                if len(lst_right_candidate) == 0:
                    """ Higher frequency """
                    max_frequency = len(lst_left_candidate[0].sentence_id)
                    candidate_max_frequency = lst_left_candidate[0]
                    for candidate in lst_left_candidate:
                        if len(candidate.sentence_id) > max_frequency:
                            max_frequency = len(candidate.sentence_id)
                            candidate_max_frequency = candidate

                    tmp_node = candidate_max_frequency
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
                elif len(lst_right_candidate) == 1:
                    tmp_node = lst_right_candidate[0]
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
                else:
                    """ Higher frequency """
                    max_frequency = len(lst_right_candidate[0].sentence_id)
                    candidate_max_frequency = lst_right_candidate[0]
                    for candidate in lst_right_candidate:
                        if len(candidate.sentence_id) > max_frequency:
                            max_frequency = len(candidate.sentence_id)
                            candidate_max_frequency = candidate

                    tmp_node = candidate_max_frequency
                    tmp_node.sentence_id.append(SW(i_sentence_id, i))
                    tmp_node.append_head(pre_node)
                    lst_recent_inserted_node.append(tmp_node)
                    pre_node.append_tail(tmp_node)
                    pre_node = tmp_node
        i += 1
    tmp_node.append_tail(e_node)
    e_node.append_head(tmp_node)
    e_node.sentence_id.append(SW(i_sentence_id, len(lst_word_pos) + 1))


def get_all_path_between_2_nodes(i_max_node, curr_node, tmp_arr, tmp_unique_set, tmp_arr_len, available_path_node, node_end_id):
    if None == curr_node:
        return
    b_check_duplicate = 0
    for i in range(tmp_arr_len):
        try:
            if curr_node.i_node_id == tmp_arr[i].i_node_id:
                b_check_duplicate = 1
                break
        except:
            b_check_duplicate = 1
            break
    if b_check_duplicate == 1:
        return
    if tmp_arr_len > i_max_node:
        return
    if len(available_path_node) >= 5000:
        return
    tmp_arr[tmp_arr_len] = curr_node
    tmp_arr_len += 1

    if curr_node.i_node_id == node_end_id:
        if tmp_arr_len >= 2:
            available_path_node.append(tmp_arr[: tmp_arr_len])
    else:
        for node in set(curr_node.tails):
            get_all_path_between_2_nodes(i_max_node, node, tmp_arr, tmp_unique_set, tmp_arr_len, available_path_node, node_end_id)


def generate_available_sentence(i_max_node, curr_node, tmp_arr, tmp_unique_set, tmp_arr_len, available_sentence_node):
    if None == curr_node:
        return
    b_check_duplicate = 0
    for i in range(tmp_arr_len):
        try:
            if curr_node.i_node_id == tmp_arr[i].i_node_id:
                b_check_duplicate = 1
                break
        except:
            b_check_duplicate = 1
            break
    if b_check_duplicate == 1:
        return
    if tmp_arr_len > i_max_node:
        return
    if len(available_sentence_node) >= 5000:
        return
    tmp_arr[tmp_arr_len] = curr_node
    tmp_arr_len += 1

    if curr_node.get_text() == 'n-End':
        if tmp_arr_len >= 3:
            available_sentence_node.append(tmp_arr[: tmp_arr_len])
    else:
        for node in curr_node.tails:
            generate_available_sentence(i_max_node, node, tmp_arr, tmp_unique_set, tmp_arr_len, available_sentence_node)


def remove_duplicates(values):
    output = []
    seen = set()
    for value in values:
        # If value has not been encountered yet,
        # ... add it to both list and set.
        if value not in seen:
            output.append(value)
            seen.add(value)
    return output


def extract_frequent_words(lst_similar_tagged_sentences, lst_stop_words):
    lst_length = len(lst_similar_tagged_sentences)
    lst_all_word = []
    lst_frequent_words = []
    for tag_sen in lst_similar_tagged_sentences:
        set_unique_word = set()
        for word in tag_sen:
            if word[0].lower().strip() not in lst_stop_words:
                # lst_all_word.append(word[0].lower().strip())
                set_unique_word.add(word[0].lower().strip())
        lst_all_word.extend(list(set_unique_word))
    word_counter = Counter(lst_all_word)
    for k, v in word_counter.items():
        if v >= lst_length:
            lst_frequent_words.append(k)
    return lst_frequent_words


def re_rank_path_use_frequent_words(available_sentences_nodes, lst_frequent_words):
    for path in available_sentences_nodes:
        plain_sentence = path[1].strip().lower()
        lst_word = plain_sentence.split(' ')
        set_word = set(lst_word)
        i_c = 0
        for word in set_word:
            if word in lst_frequent_words:
                i_c += 1
        # path[0] += path[0] + ((i_c / (1 * len(lst_frequent_words))) * abs(path[0]))
        # path[0] *= 1 - (i_c / (len(lst_frequent_words) + 1))
        new_path_weight = path[0] * (1 - (i_c / (len(lst_frequent_words) + 1)))
        # new_path_weight = path[0] * (1 - (i_c / (len(lst_frequent_words))))
        path[0] = [path[0], new_path_weight]


def action(lst_similar_tagged_sentences, lst_stop_words):
    i_general_node_id = [0]
    lst_node = []
    """ Start and End node """
    start_node = NODE(['n-Start', 'n-Start'])
    start_node.i_node_id = i_general_node_id[0]
    i_general_node_id[0] += 1
    lst_node.append(start_node)
    end_node = NODE(['n-End', 'n-End'])

    i_sentence_id = 1
    for lst_word_pos in lst_similar_tagged_sentences:
        add_sentence_to_graph(i_sentence_id, lst_word_pos, lst_node, i_general_node_id, start_node, end_node, lst_stop_words)
        i_sentence_id += 1

    end_node.i_node_id = i_general_node_id[0]
    i_general_node_id[0] += 1
    lst_node.append(end_node)

    edge_weigh = []
    i_lst_len = len(lst_node)
    for i in range(0, i_lst_len):
        edge_weigh.append([])
        for j in range(0, i_lst_len):
            edge_weigh[i].append(0)

    for i in range(0, i_lst_len):
        for tail in lst_node[i].tails:
            edge_weigh[i][tail.i_node_id] += 1
        """ Remove duplicated tail """
        lst_node[i].tails = remove_duplicates(lst_node[i].tails)

    """ Calculate edge weight """
    for i in range(0, i_lst_len):
        freq_i = len(lst_node[i].sentence_id)
        set_i = set()
        for sen_word in lst_node[i].sentence_id:
            set_i.add(sen_word.i_sentence_id)
        for j in range(0, i_lst_len):
            if edge_weigh[i][j] > 0:
                freq_j = len(lst_node[j].sentence_id)
                set_j = set()
                for sen_word in lst_node[j].sentence_id:
                    set_j.add(sen_word.i_sentence_id)

                set_i_j = set_i & set_j
                if len(set_i_j) > 0:
                    sum_diff = 0
                    for sentence_id in set_i_j:
                        word_i_id = 0
                        word_j_id = 0
                        for sen_word in lst_node[i].sentence_id:
                            if sen_word.i_sentence_id == sentence_id:
                                word_i_id = sen_word.i_word_id + 1
                                break
                        for sen_word in lst_node[j].sentence_id:
                            if sen_word.i_sentence_id == sentence_id:
                                word_j_id = sen_word.i_word_id + 1
                                break
                        diff = word_i_id - word_j_id
                        if diff > 0:
                            diff = 0
                        if diff < 0:
                            sum_diff += (diff ** (-1))
                    if sum_diff == 0:
                        edge_weigh[i][j] = [0, freq_i, freq_j]
                    else:
                        edge_weigh[i][j] = [sum_diff, freq_i, freq_j]
                else:
                    edge_weigh[i][j] = [0, freq_i, freq_j]

    """ Generate available sentences """
    k = [None] * 500
    tmp_unique_set = set()
    available_sentences_nodes = []
    generate_available_sentence(i_lst_len, lst_node[0], k, tmp_unique_set, 0, available_sentences_nodes)

    """ Remove duplicated sentences """
    tmp_check_dup1 = []
    tmp_check_dup2 = []
    for tmp_avai_sen in available_sentences_nodes:
        tmp_avai_plain_sen = ''
        for tmp_avai_sen_node in tmp_avai_sen:
            tmp_avai_plain_sen += tmp_avai_sen_node.get_text() + ' '
        if tmp_avai_plain_sen in tmp_check_dup1:
            tmp_check_dup2.append(tmp_avai_sen)
        else:
            tmp_check_dup1.append(tmp_avai_plain_sen)
    for dup_avai_sen in tmp_check_dup2:
        available_sentences_nodes.remove(dup_avai_sen)

    """ Calculate generated sentences weight """
    for i in range(0, len(available_sentences_nodes)):
        tmp_sentence_weight = 0
        tmp_sentence_text = ''
        b_check_have_verb = 1000000

        for j in range(1, len(available_sentences_nodes[i])):
            if available_sentences_nodes[i][j - 1].s_pos_tag in verb_pos_set:
                b_check_have_verb = 1
            sum_diff = edge_weigh[available_sentences_nodes[i][j - 1].i_node_id][available_sentences_nodes[i][j].i_node_id][0]
            freq_i = edge_weigh[available_sentences_nodes[i][j - 1].i_node_id][available_sentences_nodes[i][j].i_node_id][1]
            freq_j = edge_weigh[available_sentences_nodes[i][j - 1].i_node_id][available_sentences_nodes[i][j].i_node_id][2]

            tmp_sentence_text += available_sentences_nodes[i][j].get_text() + ' '
            tmp_sentence_weight += ((freq_i + freq_j) / (sum_diff * freq_i * freq_j))

        tmp_sentence_weight /= len(available_sentences_nodes[i]) - 2
        available_sentences_nodes[i] = [tmp_sentence_weight * b_check_have_verb] + [tmp_sentence_text.replace(' n-End ', '').strip()] + available_sentences_nodes[i]

    """ Sort generated sentences by length """
    available_sentences_nodes = sorted(available_sentences_nodes, key=lambda item: len(item), reverse=False)

    """ Take top 50 sentences """
    if len(available_sentences_nodes) > 50:
        available_sentences_nodes = available_sentences_nodes[: 50]
    else:
        available_sentences_nodes = available_sentences_nodes[:len(available_sentences_nodes)]

    """ Re-rank path using frequent words """
    lst_frequent_words = extract_frequent_words(lst_similar_tagged_sentences, lst_stop_words)
    re_rank_path_use_frequent_words(available_sentences_nodes, lst_frequent_words)
    available_sentences_nodes = sorted(available_sentences_nodes, key=lambda item: (item[0][1], item[0][0]), reverse=True)

    compress_result = ''
    try:
        compress_result = available_sentences_nodes[0][1]
    except:
        pass
    return compress_result
