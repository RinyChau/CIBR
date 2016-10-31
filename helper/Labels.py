def convert_to_dic(labels, probs):
    for i in range(len(probs) - 1):
        if probs[i] < probs[i + 1]:
            raise Exception("probability is not in descending order")
    label_dic = {}
    label_base = 'label{}'
    prob_base = 'prob{}'
    length = len(labels)
    for i in range(length):
        label = labels[i].split(',')[0]
        prob = float(probs[i])
        rank = i + 1
        label_key = label_base.format(rank)
        prob_key = prob_base.format(rank)
        label_dic[label_key] = label
        label_dic[prob_key] = prob
    return label_dic


def convert_to_label_array(labels):
    label_array = []
    label_base = 'label{}'
    for rank in range(1, 100):
        label_key = label_base.format(rank)
        if label_key not in labels:
            break
        label_array.append(labels[label_key])
    return label_array
