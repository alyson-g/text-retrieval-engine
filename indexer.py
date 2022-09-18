import re

import numpy as np
import pandas as pd

from inverted_index import InvertedIndex
from utils import process_word


class Indexer:
    """This class is intended to be used to parse text data."""
    def __init__(
            self,
            dataset_path: str,
            dataset_name: str,
            index: InvertedIndex
    ) -> None:
        """Initialize the Indexer instance.

        :param dataset_path: The path to the dataset file
        :param dataset_name: The name of the dataset
        :param index: The inverted index that will be populated
        """
        self.index = index
        self.documents_processed = 0
        self.words_processed = 0
        self.dataset_path = dataset_path
        self.dataset_name = dataset_name

    def load_data(self) -> None:
        """Load data from a text file."""
        print(f"Starting {self.dataset_name} processing...")

        with open(self.dataset_path, "r") as file:
            document_id = None

            for line in file:
                if not line.isspace():
                    if line.startswith("<P"):
                        document_id = int(line.replace("<P ID=", "").replace(">", ""))
                    elif "</P>" in line:
                        document_id = None
                        self.documents_processed += 1
                        print(f"{self.documents_processed} documents processed")
                    else:
                        self.__process_line(document_id, line)

        print(f"Finished processing {self.dataset_name}\n")

    def __process_line(self, document_id: int, line: str) -> None:
        """Process a single line in a text file.

        :param document_id: The ID of the document being processed
        :param line: The line to be processed
        :return: None
        """
        # Strip whitespace from ends of lines
        stripped_line = line.strip()

        # Remove unicode encodings
        encoded_line = stripped_line.encode("ascii", "ignore")
        decoded_line = encoded_line.decode()

        # Split words on common punctuation
        words = re.split("\s|-|/|,|\.|\(|\)", decoded_line)

        for word in words:
            processed_word = process_word(word)
            if not processed_word or processed_word is None or processed_word.isspace():
                continue

            self.words_processed += 1
            self.index.add_word(document_id, processed_word)

    def calculate_metrics(self) -> None:
        """Calculate metrics for reporting purposes."""
        unique_words = len(list(self.index.index.keys()))

        with open(f"./output_reports/{self.dataset_name}_metric_report.txt", "w") as file:
            file.write(f"Documents processed: {self.documents_processed}\n")
            file.write(f"Collection Size: {self.words_processed}\n")
            file.write(f"Vocabulary Size: {unique_words}\n")

    def find_singleton_words(self) -> None:
        """Find words that only appear in the corpus once."""
        words = list(self.index.index.keys())

        singletons = []

        for word in words:
            index = self.index.index[word]

            if index["count"] == 1 and index["num_docs"] == 1:
                singletons.append(word)

        with open(f"./output_reports/{self.dataset_name}_singleton_report.txt", "w") as file:
            file.write(f"Number of words that appeared only once: {len(singletons)}\n\n")

            file.write("List of singletons:\n")
            file.writelines(", ".join(singletons))

    def find_frequencies(self) -> None:
        """Find the collection and document frequency of each word."""
        words = list(self.index.index.keys())

        # Find collection frequency
        counts = [self.index.index[word]["count"] for word in words]
        sorted_counts = sorted(counts)
        sorted_count_indices = np.argsort(counts)

        # Resort words by collection frequency
        sorted_words = np.array(words)[sorted_count_indices]

        # Find document frequency
        doc_counts = [self.index.index[word]["num_docs"] for word in words]
        sorted_doc_counts = np.array(doc_counts)[sorted_count_indices]

        # Put the most frequent words in a DataFrame to make it easy to print
        df = pd.DataFrame(
            zip(sorted_words, sorted_counts, sorted_doc_counts),
            columns=["word", "collection_frequency", "document_frequency"]
        )

        df.sort_values(by="collection_frequency", inplace=True, ascending=False)
        df.reset_index(inplace=True, drop=True)
        df.index += 1

        df.to_csv(
            f"./output_reports/{self.dataset_name}_frequency_report.csv",
            index_label="rank"
        )
