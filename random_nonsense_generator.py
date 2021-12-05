import argparse
from itertools import product
import random


# definition of common syllable building blocks
_first_place_consonants = list("bcdfghkmpswz") + ["ch"]
_second_place_consonants = list("lnrtv")
_solo_consonants = list("jxq")
_vowel_like_consonants = list("lr")
_pairable_vowels = list("aeiou")
_solo_vowels = list("y")
_vowel_pairs = [f"{c1}{c2}" for c1, c2 in product(*[_pairable_vowels]*2)]


# possible syllable patterns with their probabilities
# 1 = consonant that can stand on the first place in a pair of consonants
# 2 = consonant that can stand on the second place in a pair of consonants
# c = any cosonant
# l = consonants that can act like a vowel under some special circumstances
# p = vowel pair
# v = vowel
_syllable_patterns = (
        ("12v", 40),   # e.g. MNA
        ("12p", 10),   # e.g. MNAE
        ("12vc", 1),   # e.g. MRAZ
        ("1l", 5),     # e.g. MR
        ("1l1", 1),    # e.g. MRZ
        ("1v2c", 3),   # e.g. MATZ
        ("cpc", 3),    # e.g. XAEN
        ("cp", 25),    # e.g. XAE
        ("cv", 70),    # e.g. XA
        ("cvc", 30),   # e.g. XAN
        ("p", 5),      # e.g. AE
        ("pc", 1),     # e.g. AEX
        ("v", 10),     # e.g. A
        ("vc", 15)     # e.g. AX
)

class PatternError(Exception):
        """
        Error during proccess of translation from pattern to letter
        """


def _get_1():
        return random.choice(_first_place_consonants)


def _get_2():
        return random.choice(_second_place_consonants)


def _get_c():
        _chosen_list = random.choices(
                               population = [_first_place_consonants,
                                             _second_place_consonants,
                                             _vowel_like_consonants,
                                             _solo_consonants],
                               weights = [40, 5, 35, 1]
                       )[0]
        return random.choice(_chosen_list)


def _get_l():
        return random.choice(_vowel_like_consonants)


def _get_p():
        return random.choice(_vowel_pairs)


def _get_v():
        return random.choice(_pairable_vowels + _solo_vowels)


def get_letter(pattern_symbol: str) -> str:
        if len(pattern_symbol) != 1:
                raise PatternError(
                        f"Expected single char as pattern symbol, got '{pattern_symbol}' instead"
                )
        try:
                return {
                        "1": _get_1,
                        "2": _get_2,
                        "c": _get_c,
                        "l": _get_l,
                        "p": _get_p,
                        "v": _get_v
                }[pattern_symbol]()
        except KeyError:
                raise PatternError(
                                f"Not a valid pattern symbol: '{pattern_symbol}'"
                ) 


def get_syllable() -> str:
        """
        generates random syllable
        """
        # to prevent too long vowel cluster, syllable cannot start with vowel
        # if the previous one ends with one
        can_start_with_vowel = get_syllable.__dict__.get("can_start_with_vowel", True)
        # similar one with consonants
        can_start_with_consonant = get_syllable.__dict__.get("can_start_with_consonant", True)


        # pick up next syllable pattern (nearly) randomly
        pattern = ""
        while not pattern:
                pattern_candidate = random.choices(
                                        population=[p[0] for p in _syllable_patterns],
                                        weights=[p[1] for p in _syllable_patterns]
                                    )[0]
                # check whther first letter is not a forbidden vowel
                if ((can_start_with_vowel or pattern_candidate[0] not in "vp")
                    and
                    (can_start_with_consonant or pattern_candidate[0] not in "12cl")):
                        pattern = pattern_candidate

        # generate random syllable based on the given pattern
        syllable = "".join(get_letter(pattern_symbol=c) for c in pattern)

        # save metadata about last generated vowel in the function object
        _all_vowels = _pairable_vowels + _solo_vowels
        get_syllable.can_start_with_vowel = syllable[-1] not in _all_vowels
        get_syllable.can_start_with_consonant = syllable[-1] in _all_vowels or \
                                                syllable[-2] in _all_vowels

        return syllable


def get_word() -> str:
        """
        generates word by joining random number of syllables
        """
        number_of_syllables = random.choices(
                                population=[1,  2,  3,  4,  5],
                                weights=   [20, 80, 50, 2, 1]
                              )[0]

        get_syllable.can_start_with_vowel = True
        get_syllable.can_start_with_consonant = True

        return "".join(get_syllable() for _ in range(number_of_syllables))


def get_sentence() -> str:
        """
        generates sentence by joining random number of words
        """
        number_of_words = random.choices(
                                population=[1, 2, 3,  4,  5,  6,  7,  8, 9, 10],
                                weights=   [1, 3, 20, 25, 70, 40, 10, 3, 1, 1 ]
                          )[0]
        list_of_words = [get_word() for _ in range(number_of_words)]

        # capitalize the first word of sentence
        list_of_words[0] = list_of_words[0].title()

        # insert comma (or not)
        if number_of_words > 3:
                # after first word, use 30% chance
                if random.choice(range(0, 3)) == 1:
                        list_of_words[0] += ","

                # for the rest of the words, let there be a 5% chance of comma after the word
                for i in range(min(5, number_of_words), number_of_words-1):
                        if random.choice(range(0, 20)) == 1:
                                list_of_words[i] += ","

        # add interpunction to the end of the sentence
        list_of_words[-1] += random.choices(
                                population=['.', '?', '!', '...', '?!'],
                                weights=   [85,  15,  5,   3,     1   ]
                             )[0]

        return " ".join(list_of_words)


def main() -> None:
        """
        prints random sentences to output in neverending loop
        """
        parser = argparse.ArgumentParser(description="Generate the random nonsense text")
        parser.add_argument('-n', '--number_of_sentences', type=int, default=42,
                        help='How many nonsense sentences the script will generate (default is 42)')
        args = parser.parse_args()
        number_of_sentences = args.number_of_sentences

        print(*(get_sentence() for _ in range(number_of_sentences)))


# TODO unit test
if __name__ == "__main__":
    main()

