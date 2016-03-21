#!/usr/bin/env python3
import argparse
from hashlib import md5
import math
import random
import string

class BitSet:
    BITS_PER_SLOT = 64
    def __init__(self, num_bits):
        self._num_bits = num_bits
        self._num_slots = int(math.ceil(num_bits / self.BITS_PER_SLOT))
        self._slots = [0] * self._num_slots

    @property
    def num_bits(self):
        return self._num_bits

    def __getitem__(self, position):
        bit_pos = self._get_slot_bit_pos(position)
        return (self._slots[self._get_slot(position)] & (1 << bit_pos)) >> bit_pos

    def __setitem__(self, position, value):
        bit_pos = self._get_slot_bit_pos(position)
        mask = 1 << bit_pos
        if value == 0:
            self._slots[self._get_slot(position)] &= ~mask
        else:
            self._slots[self._get_slot(position)] |= mask

    def __int__(self):
        result = 0
        for slot in range(self._num_slots):
            result |= (self._slots[slot] << (self.BITS_PER_SLOT * slot))
        return result

    def _get_slot(self, position):
        return position // self.BITS_PER_SLOT

    def _get_slot_bit_pos(self, position):
        return position % self.BITS_PER_SLOT


class BloomFilter:
    def __init__(self, capacity, error_rate):
        self._capacity = capacity
        self._error_rate = error_rate
        self._m = self._compute_m(self._capacity, error_rate)
        self._k = self._compute_k(self._capacity, self._m)
        self._bit_set = BitSet(self._m)
        self._hash_funcs = [BloomFilter._gen_hash_func(k) for k in range(self._k)]

    def __iadd__(self, element):
        for pos in self._bit_positions(element):
            self._bit_set[pos] = 1
        return self

    def __contains__(self, element):
        return all(self._bit_set[pos] == 1 for pos in self._bit_positions(element))

    def _bit_positions(self, element):
        return [self._bit_position(hash_func(element.encode())) for hash_func in self._hash_funcs]

    def _bit_position(self, hash_value):
        return hash_value % self._bit_set.num_bits

    @staticmethod
    def _compute_m(capacity, error_rate):
        return int(math.ceil(-(capacity * math.log(error_rate) / math.log(2)**2)))

    @staticmethod
    def _compute_k(capacity, m):
        return int(math.ceil(m / capacity * math.log(2)))

    @staticmethod
    def _gen_hash_func(hash_k):
        def hash_func(element):
            hasher = md5(element)
            for _ in range(hash_k - 1):
                hasher.update(element)
            return int(hasher.hexdigest(), 16)
        return hash_func

# The code below is driver functionality to generate mispellings and test the
# bloom filter functionality.
class Mispeller:
    ERRORS = ["_insert", "_delete", "_substitute", "_transpose"]

    def __init__(self, words):
        self._words = words

    def __call__(self, word):
        mispelled_word = word
        while mispelled_word in self._words:
            action_func = Mispeller._get_mispelling_function()
            location = random.randint(0, len(word) - 1)
            mispelled_word = action_func(mispelled_word, location)
        return mispelled_word

    @staticmethod
    def _get_mispelling_function():
        return getattr(Mispeller, random.sample(Mispeller.ERRORS, 1)[0])

    @staticmethod
    def _insert(word, location):
        return word[:location] + random.sample(string.ascii_letters, 1)[0] + word[location:]

    @staticmethod
    def _delete(word, location):
        return word[:location] + word[location + 1:]

    @staticmethod
    def _substitute(word, location):
        return word[:location] + random.sample(string.ascii_letters, 1)[0] + word[location + 1:]

    @staticmethod
    def _transpose(word, location):
        if location == len(word) - 1:
            return word
        return word[:location] + word[location + 1] + word[location] + word[location + 2:]

if __name__ == "__main__":
    parser = argparse.ArgumentParser("Run some bloom filter tests")
    parser.add_argument('--false_prob', default=0.1, dest="false_prob", type=float, help="False probability rate desired. Real-valued between 0 and 1.")
    parser.add_argument('--words', default="/usr/share/dict/words", dest="words_file", help="A dictionary file to use.")
    parser.add_argument('--mispellings', default=1000, dest="num_mispellings", help="Number of mispellings to run the filter against.")
    parser.add_argument('--seed', default=42, dest="seed", help="Number used to seed the random number generator.")
    args = parser.parse_args()

    random.seed(args.seed)

    # Carying the entire wordlist in memory defeats the purpose of a bloom
    # filter for spell checking - however, retaining the list allows us to
    # create mispellings for testing purposes.
    with open(args.words_file) as f:
        all_words = [word.strip() for word in f]

    bloom = BloomFilter(len(all_words), args.false_prob)
    for word in all_words:
        bloom += word

    mispell_word = Mispeller(all_words)
    mispellings = list(map(mispell_word, random.sample(all_words, args.num_mispellings)))
    mispellings_detected = list(filter(lambda x: x not in bloom, mispellings))
    mispellings_undetected = list(filter(lambda x: x in bloom, mispellings))

    print("Loaded {} words".format(len(all_words)))
    print("There were {} mispellings generated.".format(len(mispellings)))
    print("There were {} mispellings detected.".format(len(mispellings_detected)))
    print("There were {} mispellings missed.".format(len(mispellings_undetected)))
    print(mispellings_undetected)
