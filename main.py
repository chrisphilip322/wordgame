from collections import defaultdict
import json
import random

check=r'&#10003;'
arrow=r'&#129112;'
cross=r'&#215;'
lookup = [check, cross, arrow]


htmlFront = '''\
<html>
    <head>
<style>
td:first-child {
    border: 2px solid black;
}
table, th, td {
      border: 1px solid black;
}
td {
    width: 20%;
    text-align: center;
    font-size: 10em;
}
table {
    width: 100%;
    height: 25%; 
}
</style>
    </head>
    <body>'''

htmlBack = '''\
    </body>
</html>'''

htmlTemplate = r'''
<table style="page-break-before: always;">
    <tr>
    <td>{0}</td>
    <td>{1}</td>
    <td>{2}</td>
    <td>{3}</td>
    <td>{4}</td>
    </tr>
</table>
<table style="width: 100%; height: 25%;">
    <tr>
    <td>{5}</td>
    <td>{6}</td>
    <td>{7}</td>
    <td>{8}</td>
    <td>{9}</td>
    </tr>
</table>
<table style="width: 100%; height: 25%;">
    <tr>
    <td>{10}</td>
    <td>{11}</td>
    <td>{12}</td>
    <td>{13}</td>
    <td>{14}</td>
    </tr>
</table>
<table style="width: 100%; height: 25%; page-break-after: always;">
    <tr>
    <td>{15}</td>
    <td>{16}</td>
    <td>{17}</td>
    <td>{18}</td>
    <td>{19}</td>
    </tr>
</table>
'''

def grouper(iterable, n):
    "Collect data into non-overlapping fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, fillvalue='x') --> ABC DEF Gxx
    # grouper('ABCDEFG', 3, incomplete='strict') --> ABC DEF ValueError
    # grouper('ABCDEFG', 3, incomplete='ignore') --> ABC DEF
    args = [iter(iterable)] * n
    return zip(*args, strict=True)

def gen_sequences(l, options):
    if l == 0:
        yield []
    for i, v in enumerate(options):
        if v > 0:
            options[i] -= 1
            for s in gen_sequences(l-1, options):
                yield [i] + s
            options[i] += 1


def validate(word, sequence, candidate):
    chars = dict(enumerate(word))
    for i, (s, c) in enumerate(zip(sequence, candidate)):
        if s == 0:  # must match
            if chars[i] != c:
                return False
            else:
                del chars[i]
        elif chars[i] == c:
            return False
    for i, (s, c) in enumerate(zip(sequence, candidate)):
        if s == 2:  # must be elsewhere
            index = next((index for index, char in chars.items() if char == c), None)
            if index is None:
                return False
            else:
                del chars[index]
    for i, (s, c) in enumerate(zip(sequence, candidate)):
        if s == 1:  # must not match
            if c in chars.values():
                return False
    return True


def compare_all(s, words):
    for w1 in words:
        for w2 in words:
            if validate(w1, s, w2):
                yield w1, w2


with open('words.txt') as f:
    words = f.read().splitlines()

all_seqs = list(gen_sequences(5, [3,3,3]))


def rank_sequences():
    for s in all_seqs:
        print(','.join(str(x) for x in s), *(','.join(pair) for pair in compare_all(s, words)))


def load_output():
    with open('output.json') as f:
        raw = json.load(f)
    seq2word2words = defaultdict(lambda: defaultdict(list))
    word2seq2words = defaultdict(lambda: defaultdict(list))
    for raw_seq, raw_word2words in raw.items():
        seq = ','.join(str(raw_seq).rjust(5, '0'))
        for w1, raw_words in raw_word2words.items():
            for w2 in grouper(raw_words, 5):
                seq2word2words[seq][w1].append(w2)
                word2seq2words[w1][seq].append(w2)
    return seq2word2words, word2seq2words

def load_best_sequences(n):
    seq2word2words, word2seq2words = load_output()
    ranks = [(sum(len(words) for words in word2word.values()), seq) for seq, word2word in seq2word2words.items()]
    ranks.sort()
    ranks.reverse()
    return [seq for _, seq in ranks[:n]]


def print_html(seqs):
    print(htmlFront)
    q = []
    for seq in seqs:
        q += seq
        if len(q) == 20:
            print(htmlTemplate.format(*(lookup[i] for i in q)))
            q = []
    print(htmlBack)


def rank_words(seqs):
    seq2word2words, word2seq2words = load_output()
    best_seqs = frozenset(load_best_sequences(100))
    ranks = [(len(seq2words.keys() & best_seqs), word) for word, seq2words in word2seq2words.items()]
    ranks.sort()
    ranks.reverse()
    for rank, word in ranks:
        print(rank, word)
    # for w1 in words:
    #     print(len([1 for seq in seqs for w2 in words if validate(w1, seq, w2)]), w1)


def load_word_ranks():
    with open('word_ranks.txt') as f:
        lines = [line.split() for line in f.read().splitlines()]
    return [(int(rank), word) for rank, word in lines]


def prob_union(probs):
    p = 0
    for p2 in probs:
        p = p2 + (1 - p2) * p
    return p


word_ranks = load_word_ranks()
for _ in range(100):
    sample = random.sample(word_ranks, 4)
    print(prob_union([rank/100 for rank, word in sample]))
