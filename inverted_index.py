class InvertedIndex:
    def __init__(self):
        self.index = {}

    def add_word(self, document_id: int, word: str):
        """Add a word to the index."""
        if word in self.index.keys():
            self._add_existing_word(document_id, word)
        else:
            self._add_new_word(document_id, word)

    def _add_existing_word(self, document_id: int, word: str):
        """Add a word that already exists in the index."""
        doc_list = self.index[word]["doc_list"]

        if document_id not in doc_list.keys():
            doc_list[document_id] = 1
            self.index[word]["num_docs"] += 1
        else:
            doc_list[document_id] += 1

        self.index[word]["count"] += 1

    def _add_new_word(self, document_id: int, word: str):
        """Add a new word to the index."""
        doc_list = {"size": 1, document_id: 1}

        self.index[word] = {
            "count": 1,
            "num_docs": 1,
            "doc_list": doc_list
        }
