import re
import string
from typing import List

from nltk.corpus import stopwords
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize


class Processor:
    """Processes text using either simple processing methods or nltk."""
    def __init__(self, use_nltk: bool = True):
        self.use_nltk = use_nltk

        if self.use_nltk:
            self.stemmer = PorterStemmer()
            self.stop_words = set(stopwords.words("english"))

    def process_line(self, line: str) -> List[str]:
        """Process a line of text.

        :param line: The line of text
        :return: A list of clean tokens
        """
        if self.use_nltk:
            return self.__nltk_process_line(line)
        else:
            return self.__simple_process_line(line)

    def process_token(self, token: str) -> str:
        """Processes a single token.

        :param token: A token to process
        :return: The processed token
        """
        if self.use_nltk:
            return self.__nltk_process_line(token)
        else:
            return self.__simple_process_token(token)

    @staticmethod
    def __simple_process_token(token: str) -> str:
        """Removes punctuation and converts a token to lowercase.

        :param token: The token to be processed
        :return: The processed token
        """
        stripped_token = token.strip()
        return stripped_token.translate(str.maketrans('', '', string.punctuation)).lower()

    def __simple_process_line(self, line: str) -> List[str]:
        """Process a line of text using simple tokenization methods.

        :param line: A line of text
        :return: A list of clean tokens
        """
        # Strip whitespace from ends of lines
        stripped_line = line.strip()

        # Remove unicode encodings
        encoded_line = stripped_line.encode("ascii", "ignore")
        decoded_line = encoded_line.decode()

        # Split tokens on common punctuation
        tokens = re.split("\s|-|/|,|\.|\(|\)", decoded_line)

        clean_tokens = []
        for token in tokens:
            processed_token = self.__simple_process_token(token)
            if not processed_token or processed_token is None or processed_token.isspace():
                continue

            clean_tokens.append(processed_token)

        return clean_tokens

    def __nltk_process_token(self, token: str) -> str:
        """Tokenizes and stems a token using nltk.

        :param token: A token to process
        :return: The processed token
        """
        tokenized_token = word_tokenize(token)[0]
        stemmed_token = self.stemmer.stem(tokenized_token)
        return stemmed_token

    def __nltk_process_line(self, line: str) -> List[str]:
        """Process a line of text using nltk's tokenizer and stemmer.

        :param line: A line of text
        :return: A list of clean tokens
        """
        tokens = word_tokenize(line)

        clean_tokens = []

        for token in tokens:
            # Remove stop words
            if token.lower() in self.stop_words:
                continue

            # Stem token
            stemmed_token = self.stemmer.stem(token)

            # Remove non-words
            if not re.match('\W?\w+', stemmed_token):
                continue

            clean_tokens.append(stemmed_token)

        return clean_tokens
