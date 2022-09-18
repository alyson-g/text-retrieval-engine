from indexer import Indexer
from inverted_index import InvertedIndex


def main():
    for dataset_name in ["yelp", "headlines"]:
        dataset_path = f"./sample_data/{dataset_name}.txt"
        index = InvertedIndex()

        indexer = Indexer(dataset_path, dataset_name, index)
        indexer.load_data()

        lexicon_file, inverted_file = index.generate_file(dataset_name)

        indexer.calculate_metrics()
        indexer.find_singleton_words()
        indexer.find_frequencies()


if __name__ == '__main__':
    main()
