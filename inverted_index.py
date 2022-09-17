class InvertedIndex:
    def __init__(self):
        self.index = {}

    def add_word(self, document_id: int, word: str):
        """Add a word to the index."""
        if word in self.index.keys():
            self.__add_existing_word(document_id, word)
        else:
            self.__add_new_word(document_id, word)

    def __add_existing_word(self, document_id: int, word: str):
        """Add a word that already exists in the index.

        :param document_id: The ID of the document being processed
        :param word: The word in the index that should be updated
        :return: None
        """
        postings_list = self.index[word]["doc_list"]

        if document_id not in postings_list.keys():
            postings_list[document_id] = 1
            self.index[word]["num_docs"] += 1
        else:
            postings_list[document_id] += 1

        self.index[word]["count"] += 1

    def __add_new_word(self, document_id: int, word: str):
        """Add a new word to the index.

        :param document_id: The ID of the document being processed
        :param word: The new word to be added
        :return: None
        """
        postings_list = {"size": 1, document_id: 1}

        self.index[word] = {
            "count": 1,
            "num_docs": 1,
            "postings_list": postings_list
        }
