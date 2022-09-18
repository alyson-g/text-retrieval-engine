import string


def process_word(word: str) -> str:
    """Removes punctuation and converts a word to lowercase.

    :param word: The word to be processed
    :return: The processed word
    """
    stripped_word = word.strip()
    return stripped_word.translate(str.maketrans('', '', string.punctuation)).lower()
