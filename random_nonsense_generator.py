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

def start():
        """
        prints random sentences to output in neverending loop
        """
        while True:
                for c in get_sentence():
                        print(c, end="")


if __name__ == "__main__":
    start()

