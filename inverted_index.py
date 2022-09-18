from datetime import datetime
from typing import Dict, List, Tuple

import pandas as pd

from utils import process_word


class InvertedIndex:
    def __init__(self) -> None:
        """Initialize the InvertedIndex instance."""
        self.index = {}

    def add_word(self, document_id: int, word: str) -> None:
        """Add a word to the index."""
        if word in self.index.keys():
            self.__add_existing_word(document_id, word)
        else:
            self.__add_new_word(document_id, word)

    def __add_existing_word(self, document_id: int, word: str) -> None:
        """Add a word that already exists in the index.

        :param document_id: The ID of the document being processed
        :param word: The word in the index that should be updated
        :return: None
        """
        postings_list = self.index[word]["postings_list"]

        if document_id not in postings_list.keys():
            postings_list[document_id] = 1
            self.index[word]["num_docs"] += 1
        else:
            postings_list[document_id] += 1

        self.index[word]["count"] += 1

    def __add_new_word(self, document_id: int, word: str) -> None:
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

    def generate_file(
            self,
            dataset_name: str,
            byte_order: str = "big",
    ) -> Tuple[str, str]:
        """Generate lexicon and inverted files.

        :param dataset_name: The name of the dataset
        :param byte_order: The ordering of the bytes to use within the inverted file
            (either big or little)
        :return: None
        """
        now = datetime.now()
        now_str = datetime.strftime(now, "%d%m%Y-%H%M%S")

        # These arrays will be used to generate the lexicon file
        terms = []
        doc_frequencies = []
        offsets = []

        lexicon_file = f"./output_reports/{dataset_name}_lexicon_{now_str}.csv"
        inverted_file = f"./output_reports/{dataset_name}_index_{now_str}.bin"

        with open(inverted_file, "wb") as f:
            # This variable tracks the offset within the index file
            offset = 0

            for term in self.index.keys():
                terms.append(term)
                doc_frequencies.append(self.index[term]["num_docs"])
                offsets.append(offset)

                postings_list = self.index[term]["postings_list"]

                for posting in postings_list.keys():
                    if posting == "size":
                        continue

                    doc_id = int(posting)
                    frequency = postings_list[posting]

                    f.write(doc_id.to_bytes(4, byte_order))
                    f.write(frequency.to_bytes(4, byte_order))

                    offset += 8

        df = pd.DataFrame(
            zip(terms, doc_frequencies, offsets),
            columns=["term", "document_frequency", "offset"]
        )
        df.to_csv(lexicon_file, index=False)

        return lexicon_file, inverted_file

    @staticmethod
    def extract_information(
            lexicon_file: str,
            index_file: str,
            terms: List[str],
            byte_order: str = "big"
    ) -> Dict[str, pd.DataFrame]:
        """Extract information about a term or terms.

        :param lexicon_file: The name of the lexicon file
        :param index_file: The name of the index file
        :param terms: A list of terms to extract information about
        :param byte_order: The ordering of the bytes used within the inverted file
            (either big or little)
        :return: A dictionary of terms as keys and DataFrames of document IDs and their
            term frequencies as values
        """
        lexicon = pd.read_csv(lexicon_file)

        results = {}

        for term in terms:
            # Term must be preprocessed to look up in the index
            processed_word = process_word(term)

            # These variables are used to generate summary DataFrames for each term
            doc_ids = []
            frequencies = []

            row = lexicon[lexicon["term"] == processed_word]

            if row.shape[0] == 0:
                print(f"The term '{term}' was not found in the index")
                continue

            next_row = lexicon.loc[row.index + 1]

            offset = row.iloc[0, 2]
            num_bytes = next_row.iloc[0, 2] - row.iloc[0, 2]

            with open(index_file, "rb") as f:
                f.seek(offset)

                for _ in range(int(num_bytes / 8)):
                    doc_id_raw = f.read(4)
                    doc_id = int.from_bytes(doc_id_raw, byte_order)

                    frequency_raw = f.read(4)
                    frequency = int.from_bytes(frequency_raw, byte_order)

                    doc_ids.append(doc_id)
                    frequencies.append(frequency)

            df = pd.DataFrame(zip(doc_ids, frequencies), columns=["doc_id", "frequency"])
            results[term] = df

        return results
