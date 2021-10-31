import random
import sys
import time

def get_syllable():
        """
        generates random syllable
        """
        pass


def get_word():
        """
        generates word by joining random number of syllables
        """
        pass


def get_sentence():
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
                                weights=   [75,  15,  5,   4,     1   ]
                             )[0]

        return " ".join(list_of_words)


def start():
        """
        prints random sentences to output in neverending loop
        """
        while True:
                for c in get_sentence():
                        print(c, end="")
                        sys.stdout.flush()
                        time.sleep(.01)
                print()


if __name__ == "__main__":
    start()

