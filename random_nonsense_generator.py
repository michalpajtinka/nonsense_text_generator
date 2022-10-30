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


# how many syllables can word consist of
_word_lengths = (
    (1, 20),
    (2, 80),
    (3, 50),
    (4, 2),
    (5, 1),
)


# how many words can sentence consist of
_sentence_lengths = (
    (1, 1),
    (2, 3),
    (3, 20),
    (4, 25),
    (5, 70),
    (6, 40),
    (7, 10),
    (8, 3),
    (9, 1),
    (10, 1)
)


# word building blocks and their probabilities (loosely inspired by frequencies
# of letters in English)
_vowels = (
    ("a", 85),
    ("e", 112),
    ("i", 75),
    ("o", 72),
    ("u", 36),
    ("y", 1)
)
_vowel_pairs = (
    ("ae", 40),
    ("ia", 20),
    ("ie", 20),
    ("iu", 20),
    ("ea", 30),
    ("ei", 10),
    ("eu", 1),
    ("oo", 5),
)
_consonants = (
    ("b", 21),
    ("c", 15),
    ("d", 34),
    ("f", 18),
    ("g", 5),
    ("gl", 15),
    ("gr", 15),
    ("h", 15),
    ("ch", 45),
    ("chr", 5),
    ("chl", 5),
    ("j", 1),
    ("k", 11),
    ("l", 55),
    ("m", 30),
    ("n", 67),
    ("p", 32),
    ("qu", 5),
    ("r", 75),
    ("s", 30),
    ("sh", 20),
    ("sk", 20),
    ("sp", 20),
    ("st", 20),
    ("t", 40),
    ("th", 15),
    ("tr", 25),
    ("tl", 15),
    ("v", 10),
    ("w", 10),
    ("wh", 15),
    ("wr", 20),
    ("wl", 20),
    ("x", 3),
    ("z", 1)
)
_ending_only_consonants = (
    ("ck", 15),
    ("sh", 15) 
) + tuple(c for c in _consonants if len(c[0]) == 1 and c[0] not in "xz")


# these letters can follow themselves inside words 
_duplicable_consonants = list("bdfklmnprst")


# possible syllable patterns with their probabilities:
# c = consonant
# e = ending only consonant
# p = vowel pair
# v = vowel
_syllable_patterns = (
    ("cv", 100),   # e.g. PA
    ("cve", 20),   # e.g. PAN
    ("cp", 10),    # e.g. PIE
    ("cpe", 1),    # e.g. PIEN
    ("v", 10),     # e.g. A
    ("ve", 15)     # e.g. AP
)


class PatternError(Exception):
        """
        Error during pattern to letter translation
        """


def _get_c():
    return WSCC.get_random_element(_consonants)


def _get_e():
    return WSCC.get_random_element(_ending_only_consonants)


def _get_p():
    return WSCC.get_random_element(_vowel_pairs)


def _get_v():
    return WSCC.get_random_element(_vowels)


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
    "c": _get_c,
    "e": _get_e,
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
           and pattern[1] in "ce"):
        # repeat in case of not allowed letter duplication
        syllable = _generate_syllable(pattern)

    # save metadata about last generated vowel in the function object
    get_syllable.can_start_with_vowel = (syllable[-1] not in
                                         WSCC.get_population(_vowels))
    get_syllable.can_start_with_consonant = (syllable[-1] in WSCC.get_population(_vowels)
                                             or syllable[-2] in WSCC.get_population(_vowels))
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
    number_of_words = WSCC.get_random_element(_sentence_lengths) 
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

