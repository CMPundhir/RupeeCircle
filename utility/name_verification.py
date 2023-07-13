from difflib import SequenceMatcher


def match_name(name1, name2):
    first_name = name1.split(' ')
    second_name = name2.split(' ')
    for i in first_name:
        for j in second_name:
            matching = SequenceMatcher(None, i, j).ratio()
            reverse_matching = SequenceMatcher(None, i, j).ratio()
            if matching or reverse_matching > 0.7:
                return True
    return False