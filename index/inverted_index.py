from collections import Counter
from datetime import datetime
import logging
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from processor import Processor


logger = logging.getLogger(__name__)


class InvertedIndex:
    def __init__(self) -> None:
        """Initialize the InvertedIndex instance."""
        self.index = {}
        self.num_docs = 0
        self.num_terms = 0

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

        self.index[word] = {"count": 1, "num_docs": 1, "postings_list": postings_list}
        self.num_terms += 1

    def generate_file(
        self,
        dataset_name: str,
        byte_order: str = "big",
    ) -> Tuple[str, str, str]:
        """Generate lexicon and inverted files.

        :param dataset_name: The name of the dataset
        :param byte_order: The ordering of the bytes to use within the inverted file
            (either big or little)
        :return: A tuple containing the names of the generated files
        """
        now = datetime.now()
        now_str = datetime.strftime(now, "%d%m%Y-%H%M%S")

        # These lists will be used to generate the lexicon file
        terms = list(self.index.keys())
        doc_frequencies = []
        offsets = []
        idfs = []

        # These variables will be used to generate the document vector length file
        doc_vector_lengths = np.zeros((self.num_docs,))

        lexicon_file = f"./output_reports/{dataset_name}_lexicon_{now_str}.csv"
        inverted_file = f"./output_reports/{dataset_name}_index_{now_str}.bin"
        document_length_file = f"./output_reports/{dataset_name}_document_length_{now_str}.csv"

        with open(inverted_file, "wb") as f:
            # This variable tracks the offset within the index file
            offset = 0

            for i in range(len(terms)):
                term = terms[i]

                terms.append(term)
                doc_frequencies.append(self.index[term]["num_docs"])
                offsets.append(offset)

                postings_list = self.index[term]["postings_list"]
                doc_frequency = len(postings_list) - 1
                idf = np.log2(self.num_docs / doc_frequency)
                idfs.append(idf)

                for posting in postings_list.keys():
                    if posting == "size":
                        continue

                    doc_id = int(posting)

                    frequency = postings_list[posting]
                    doc_vector_lengths[doc_id - 1] += np.square(frequency * idf)

                    f.write(doc_id.to_bytes(4, byte_order))
                    f.write(frequency.to_bytes(4, byte_order))

                    offset += 8

        doc_vector_lengths = np.sqrt(doc_vector_lengths)

        doc_lengths_df = pd.DataFrame(
            zip(list(range(1, self.num_docs + 1)), doc_vector_lengths),
            columns=["doc_id", "euclidean_length"],
        )
        doc_lengths_df.to_csv(document_length_file, index=False)

        df = pd.DataFrame(
            zip(terms, doc_frequencies, idfs, offsets),
            columns=["term", "document_frequency", "inverse_document_frequency", "offset"],
        )
        df.to_csv(lexicon_file, index=False)

        return lexicon_file, inverted_file, document_length_file

    @staticmethod
    def extract_information(
        lexicon_file: str,
        index_file: str,
        terms: List[str],
        processor: Processor,
        byte_order: str = "big",
    ) -> Dict[str, pd.DataFrame]:
        """Extract information about a term or terms.

        :param lexicon_file: The name of the lexicon file
        :param index_file: The name of the index file
        :param terms: A list of terms to extract information about
        :param byte_order: The ordering of the bytes used within the inverted file
            (either big or little)
        :param processor: The document processor object
        :return: A dictionary of terms as keys and DataFrames of document IDs and their
            term frequencies as values
        """
        lexicon = pd.read_csv(lexicon_file)

        results = {}

        for term in terms:
            # Term must be preprocessed to look up in the index
            processed_word = processor.process_token(term)[0]

            if processed_word is None:
                continue

            # These variables are used to generate summary DataFrames for each term
            doc_ids = []
            frequencies = []

            row = lexicon[lexicon["term"] == processed_word]

            if row.shape[0] == 0:
                logging_tools.info(f"The term '{term}' was not found in the index")
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

    @staticmethod
    def tf_idf(
        lexicon_file: str,
        index_file: str,
        query_terms: List[str],
        num_docs: int,
        byte_order: str = "big",
    ) -> Tuple[np.array, np.array]:
        """Calculate the tf-idf matrix for a given set of documents and query terms.

        :param lexicon_file: The name of the lexicon file
        :param index_file: The name of the index file
        :param query_terms: A list of terms extracted from the query
        :param num_docs: The total number of documents in the collection
        :param byte_order: The ordering of the bytes used within the inverted file
            (either big or little)

        :return: A tuple of the calculated tf-idf matrix and the idf weights for each document
        """
        lexicon = pd.read_csv(lexicon_file)
        num_terms = len(query_terms)

        tf_idfs = np.zeros((num_terms, num_docs))
        idfs = np.zeros((1, num_terms))

        for i in range(len(query_terms)):
            term = query_terms[i]

            row = lexicon[lexicon["term"] == term]

            if row.shape[0] == 0:
                logging_tools.info(f"The term '{term}' was not found in the index")
                continue

            next_row = lexicon.loc[row.index + 1]

            offset = row.iloc[0, 3]
            num_bytes = next_row.iloc[0, 3] - row.iloc[0, 3]

            doc_frequency = 0
            with open(index_file, "rb") as f:
                f.seek(offset)

                for _ in range(int(num_bytes / 8)):
                    doc_id_raw = f.read(4)
                    doc_id = int.from_bytes(doc_id_raw, byte_order)

                    frequency_raw = f.read(4)
                    tf = int.from_bytes(frequency_raw, byte_order)

                    doc_frequency += 1
                    tf_idfs[i, doc_id - 1] = tf

            idf = lexicon[lexicon["term"] == term]["inverse_document_frequency"].values[0]

            idfs[0][i] = idf
            tf_idfs[i] = tf_idfs[i] * idf

        return tf_idfs, idfs

    def cosine_similarity(
        self,
        lexicon_file: str,
        index_file: str,
        doc_length_file: str,
        query: List[str],
        byte_order: str = "big",
        verbose: bool = False,
    ) -> pd.DataFrame:
        """Calculate cosine similarity.

        This method calculates cosine similarity between a given query and documents in a
        pre-computed index file.

        :param lexicon_file: The name of the lexicon file
        :param index_file: The name of the index file
        :param doc_length_file: The name of the document length file
        :param query: The tokenized query against which to calculate cosine similarity
        :param byte_order: The ordering of the bytes used within the inverted file
            (either big or little)
        :param verbose: Whether or not to print the query weights
        :return: A DataFrame of cosine similarity scores
        """
        # Calculate unique terms and their frequencies in the query
        query_counter = Counter(query)
        num_terms = len(query_counter.keys())

        # Calculate total number of documents in the collection
        doc_lengths = pd.read_csv(doc_length_file)
        num_docs = doc_lengths["doc_id"].max()

        # Calculate tf-idf for collection
        query_terms = list(query_counter.keys())
        tf_idfs, idfs = self.tf_idf(lexicon_file, index_file, query_terms, num_docs, byte_order)

        # Calculate query tf-idf
        query_tf_idf = np.array(list(query_counter.values())).reshape((num_terms, 1))
        query_tf_idf = idfs.T * query_tf_idf
        query_tf_idf = query_tf_idf.reshape((num_terms,))

        if verbose:
            query_df = pd.DataFrame(
                zip(query_terms, query_tf_idf), columns=["term", "tf_idf_weight"]
            )
            logging_tools.info(query_df)

        # Calculate query vector length
        query_length = np.linalg.norm(query_tf_idf)

        # Transform document vector lengths
        doc_lengths_vector = doc_lengths["euclidean_length"].values

        # Finally, calculate cosine similarity
        similarity = np.dot(query_tf_idf.T, tf_idfs) / (query_length * doc_lengths_vector)
        similarity[np.isnan(similarity)] = 0

        ids = np.array(range(len(similarity))) + 1
        return pd.DataFrame(zip(ids, similarity), columns=["doc_id", "cosine_score"])
