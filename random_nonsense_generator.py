import argparse
from itertools import product
import random
from typing import Any


ElementListType = tuple[tuple[Any, int], ...] 


class WeightedElementsCollectionCache:
    class Collection:
        def __init__(self, element_list: ElementListType) -> None:
            self.population = [e[0] for e in element_list]
            self.weights = [e[1] for e in element_list]

    objects: dict[ElementListType, Collection] = {}

    @classmethod
    def get_population(cls, element_list: ElementListType) -> list[Any]:
        return cls._get_collection(element_list).population

    @classmethod
    def get_weights(cls, element_list: ElementListType) -> list[int]:
        return cls._get_collection(element_list).weights

    @classmethod
    def get_random_element(cls, element_list: ElementListType) -> Any:
        return random.choices(
            population=cls.get_population(element_list),
            weights=cls.get_weights(element_list)
        ).pop()

    @classmethod
    def _get_collection(cls, element_list: ElementListType) -> Collection:
        try:
            return cls.objects[element_list]
        except KeyError:
            cls.objects[element_list] = cls.Collection(element_list)
        return cls.objects[element_list]
# alias WeightedElementsCollectionCache to something shorter
WSCC = WeightedElementsCollectionCache


# definition of common syllable building blocks
_first_place_consonants = list("bcdfghkmpsz") + ["ch"]
_second_place_consonants = list("lnrtv")
_solo_consonants = list("jxqw")
_vowel_like_consonants = list("lr")
_vowels = list("aeiouy")
_vowel_pairs = ["ae", "ia", "ie", "iu", "oo", "uo"]


# possible syllable patterns with their probabilities:
# 1 = consonant that can stand on the first place in a pair of consonants
# 2 = consonant that can stand on the second place in a pair of consonants
# c = any cosonant
# l = consonants that can act like a vowel under some special circumstances
# p = vowel pair
# v = vowel
_syllable_patterns = (
    ("12v", 20),   # e.g. MNA
    ("12vc", 1),   # e.g. MRAZ
    ("1l1", 1),    # e.g. MRZ
    ("cv", 100),   # e.g. PA
    ("cvc", 20),   # e.g. PAN
    ("cp", 10),    # e.g. PIE
    ("cpc", 3),    # e.g. PIEN
    ("v", 10),     # e.g. A
    ("vc", 15),    # e.g. AP
    ("vlc", 5)     # e.g. ARP
)


# some additional configurations
_duplicable_consonants = list("bdfklmnprst")  # there letters can follow
                                              # themselves inside words

_word_lengths = (
    (1, 20),
    (2, 80),
    (3, 50),
    (4, 2),
    (5, 1),
)  # how many syllables can word consist of


class PatternError(Exception):
        """
        Error during pattern to letter translation
        """


def _get_1():
    return random.choice(_first_place_consonants)


def _get_2():
    return random.choice(_second_place_consonants)


def _get_c():
    _chosen_list = random.choices(
                       population = [_first_place_consonants,
                                     _second_place_consonants,
                                     _solo_consonants],
                       weights = [40, 5, 1]
                   ).pop()
    return random.choice(_chosen_list)


def _get_l():
    return random.choice(_vowel_like_consonants)


def _get_p():
    return random.choice(_vowel_pairs)


def _get_v():
    return random.choice(_vowels)


def get_letter(pattern_symbol: str) -> str:
    if len(pattern_symbol) != 1:
        raise PatternError(
            f"Expected single char as pattern symbol, got "
            f"'{pattern_symbol}' instead"
        )
    try:
        return get_letter.pattern_mapping[pattern_symbol]()
    except KeyError:
        raise PatternError(f"Not a valid pattern symbol: '{pattern_symbol}'") 
get_letter.pattern_mapping = {
    "1": _get_1,
    "2": _get_2,
    "c": _get_c,
    "l": _get_l,
    "p": _get_p,
    "v": _get_v
}


def _generate_syllable(pattern) -> str:
    return "".join(get_letter(pattern_symbol=c) for c in pattern)


def get_syllable() -> str:
    """
    generates random syllable
    """
    # to prevent too long vowel cluster, syllable cannot start with vowel
    # if the previous one ends with one
    can_start_with_vowel = get_syllable.__dict__.get(
        "can_start_with_vowel", True)
    # similar one with consonants
    can_start_with_consonant = get_syllable.__dict__.get(
        "can_start_with_consonant", True)
    # to prevent unwanted repeated letters
    last_letter = get_syllable.__dict__.get(
        "last_letter", None)

    # pick up next syllable pattern (nearly) randomly
    pattern = ""
    while not pattern:
        pattern_candidate = WSCC.get_random_element(_syllable_patterns)
        # check whether the first letter is not forbidden
        if ((can_start_with_vowel or pattern_candidate[0] not in "vp") and
            (can_start_with_consonant or pattern_candidate[0] not in "12cl")):
            pattern = pattern_candidate

    # generate random syllable based on the given pattern
    syllable = _generate_syllable(pattern)
    while (syllable[0] == last_letter
           and last_letter not in _duplicable_consonants
           and pattern[1] not in "pv"):
        # repeat in case of not allowed letter duplication
        syllable = _generate_syllable(pattern)

    # save metadata about last generated vowel in the function object
    get_syllable.can_start_with_vowel = syllable[-1] not in _vowels
    get_syllable.can_start_with_consonant = (syllable[-1] in _vowels
                                             or syllable[-2] in _vowels)
    get_syllable.last_letter = syllable[-1]
    return syllable


def get_word() -> str:
    """
    generates word by joining random number of syllables
    """
    number_of_syllables = WSCC.get_random_element(_word_lengths)

    get_syllable.can_start_with_vowel = True
    get_syllable.can_start_with_consonant = True
    get_syllable.last_letter = None

    return "".join(get_syllable() for _ in range(number_of_syllables))


def get_sentence() -> str:
    """
    generates sentence by joining random number of words
    """
    number_of_words = random.choices(
                          population=[1, 2, 3,  4,  5,  6,  7,  8, 9, 10],
                          weights=   [1, 3, 20, 25, 70, 40, 10, 3, 1, 1 ]
                      ).pop()
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
                         ).pop()

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

    print(*[get_sentence() for _ in range(number_of_sentences)])


# TODO unit test
if __name__ == "__main__":
    main()

