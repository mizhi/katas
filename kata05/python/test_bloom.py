import collections
import random

from flexmock import flexmock
import unittest

from bloom import BitSet, BloomFilter, Mispeller

class TestBitSet(unittest.TestCase):
    def test_int_turns_bitset_into_equivalent_int(self):
        TEST_PARAMS = [
            # Int representation (little endian) 0  1
            #           Slot 1          Slot 0
            #                |               |
            (0x00000000000000000000000000000000, [0, 0]),
            (0x00000000000000000000000000000001, [1, 0]),
            (0x00000000000000010000000000000000, [0, 1]),
            (0x80000000000000000000000000000000, [0, 9223372036854775808]),
            (0x81100000000401008152000001140110, [9318510579001065744, 9299933230520336640])
        ]

        for (x, slots) in TEST_PARAMS:
            with self.subTest(x = x):
                bs = BitSet(2 * BitSet.BITS_PER_SLOT)
                bs._slots = slots[:]
                self.assertEqual(x, int(bs))

    def test_get_slot_returns_correct_slot_for_bit_position(self):
        TEST_PARAMS = [
            (0, 0),
            (0, 1),
            (0, BitSet.BITS_PER_SLOT - 1),
            (1, BitSet.BITS_PER_SLOT),
            (1, BitSet.BITS_PER_SLOT + 1),
            (2, 2 * BitSet.BITS_PER_SLOT + 1)
        ]

        for (expected_slot, position) in TEST_PARAMS:
            with self.subTest(position = position):
                bs = BitSet(3 * BitSet.BITS_PER_SLOT)
                self.assertEqual(expected_slot, bs._get_slot(position))

    def test_get_bit_pos_returns_correct_bit_position_in_slot(self):
        TEST_PARAMS = [
            (0, 0),
            (1, 1),
            (BitSet.BITS_PER_SLOT - 1, BitSet.BITS_PER_SLOT - 1),
            (0, BitSet.BITS_PER_SLOT),
            (10, BitSet.BITS_PER_SLOT + 10)
        ]
        for (expected_slot_bit_pos, position) in TEST_PARAMS:
            with self.subTest(position = position):
                bs = BitSet(3 * BitSet.BITS_PER_SLOT)
                self.assertEqual(expected_slot_bit_pos, bs._get_slot_bit_pos(position))

    def test_get_item_returns_correct_bit_in_position(self):
        TEST_PARAMS = [
            (0, [0, 0], 0),
            (1, [1, 0], 0),
            (1, [1 << 1, 0], 1),
            (1, [0, 1], BitSet.BITS_PER_SLOT),
            (1, [0, 1 << 1], BitSet.BITS_PER_SLOT + 1)
        ]
        for (expected_bit, slots, position) in TEST_PARAMS:
            with self.subTest(position = position):
                bs = BitSet(2 * BitSet.BITS_PER_SLOT)
                bs._slots = slots[:]
                self.assertEqual(expected_bit, bs[position])

    def test_set_item_sets_correct_bit_in_position(self):
        TEST_PARAMS = [
            ([1, 0], 0),
            ([2, 0], 1),
            ([0, 1], BitSet.BITS_PER_SLOT),
            ([0, 1 << (BitSet.BITS_PER_SLOT - 1)], BitSet.BITS_PER_SLOT * 2 - 1),
        ]
        for (expected_slots, position) in TEST_PARAMS:
            with self.subTest(position = position):
                bs = BitSet(2 * BitSet.BITS_PER_SLOT)
                bs[position] = 1
                self.assertEqual(expected_slots, bs._slots)

    def test_set_item_clears_correct_bit_in_position(self):
        TEST_PARAMS = [
            ([0xFFFFFFFFFFFFFFFE, 0xFFFFFFFFFFFFFFFF], 0),
            ([0xFFFFFFFFFFFFFFFD, 0xFFFFFFFFFFFFFFFF], 1),
            ([0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFE], BitSet.BITS_PER_SLOT),
            ([0xFFFFFFFFFFFFFFFF, 0x7FFFFFFFFFFFFFFF], BitSet.BITS_PER_SLOT * 2 - 1),
        ]
        for (expected_slots, position) in TEST_PARAMS:
            with self.subTest(position = position):
                bs = BitSet(2 * BitSet.BITS_PER_SLOT)
                bs._slots = [0xFFFFFFFFFFFFFFFF, 0xFFFFFFFFFFFFFFFF]
                bs[position] = 0
                self.assertEqual(expected_slots, bs._slots)

class TestBloomFilter(unittest.TestCase):
    def test_hash_funcs_are_generated(self):
        m = BloomFilter._compute_m(100, 0.1)
        k = BloomFilter._compute_k(100, m)

        for k in range(0, k):
            (flexmock(BloomFilter).
             should_receive("_gen_hash_func").
             with_args(k).
             and_return(lambda w: k).
             ordered().
             once())

        bf = BloomFilter(100, 0.1)

        self.assertEqual(bf._k, len(bf._hash_funcs))
        self.assertTrue(all(isinstance(func, collections.Callable) for func in bf._hash_funcs))

        for k in range(bf._k):
            self.assertEqual(k, bf._hash_funcs[k]("".encode()))

class TestMispeller(unittest.TestCase):
    FAKE_ALL_WORDS = ["word"]

    def setUp(self):
        self.mispeller = Mispeller(self.FAKE_ALL_WORDS)

    def test_call_selects_function_and_calls_it(self):
        (flexmock(Mispeller).
         should_receive("_get_mispelling_function").
         and_return(lambda w, l: w + str(l)).once())
        (flexmock(random).
         should_receive("randint").
         and_return(0).
         once())
        self.assertEqual("word0", self.mispeller("word"))

    def test_call_keeps_going_until_word_is_mispelled(self):
        flexmock(random).should_receive("randint").and_return(0)

        (flexmock(Mispeller).
         should_receive("_get_mispelling_function").
         and_return(lambda w, l: w).once().ordered())

        (flexmock(Mispeller).
         should_receive("_get_mispelling_function").
         and_return(lambda w, l: w + str(l)).once().ordered())

        self.assertEqual("word0", self.mispeller("word"))

    def test_insert_works(self):
        TEST_PARAMS = [
            ("Iword", "word", 0),
            ("woIrd", "word", 2),
            ("wordI", "word", 4)
        ]
        flexmock(random).should_receive("sample").and_return("I").times(3)
        self.check_mispelling_function(Mispeller._insert, TEST_PARAMS)

    def test_delete_works(self):
        TEST_PARAMS = [
            ("ord", "word", 0),
            ("wod", "word", 2),
            ("wor", "word", 3)
        ]
        self.check_mispelling_function(Mispeller._delete, TEST_PARAMS)

    def test_substitute_works(self):
        TEST_PARAMS = [
            ("Iord", "word", 0),
            ("woId", "word", 2),
            ("worI", "word", 3)
        ]
        flexmock(random).should_receive("sample").and_return("I").times(3)
        self.check_mispelling_function(Mispeller._substitute, TEST_PARAMS)

    def test_substitute_works(self):
        TEST_PARAMS = [
            ("owrd", "word", 0),
            ("wrod", "word", 1),
            ("wodr", "word", 2),
            ("word", "word", 3)
        ]
        self.check_mispelling_function(Mispeller._transpose, TEST_PARAMS)

    def check_mispelling_function(self, func, test_params):
        for (expected_word, starting_word, location) in test_params:
            self.assertEqual(expected_word, func(starting_word, location))

if __name__ == "__main__":
    unittest.main()
