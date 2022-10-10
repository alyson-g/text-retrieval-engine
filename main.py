import time

from indexer import Indexer
from inverted_index import InvertedIndex
from processor import Processor


def main():
    start = time.time()

    for dataset_name in ["cord19"]:
        dataset_path = f"./sample_data/{dataset_name}.txt"
        processor = Processor()
        index = InvertedIndex()

        indexer = Indexer(dataset_path, dataset_name, processor, index)
        indexer.load_data()

        lexicon_file, inverted_file = index.generate_file(dataset_name)

        indexer.calculate_metrics()
        indexer.find_singleton_words()
        indexer.find_frequencies()

    end = time.time()

    print(f"Seconds elapsed: {end - start}")
    print(f"Minutes elapsed: {(end - start) / 60}")


if __name__ == '__main__':
    main()
