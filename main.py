from indexer import Indexer


def main():
    for dataset_name in ["yelp", "headlines"]:
        dataset_path = f"./sample_data/{dataset_name}.txt"
        indexer = Indexer(dataset_path, dataset_name)

        indexer.calculate_metrics()
        indexer.find_singleton_words()
        indexer.find_frequencies()


if __name__ == '__main__':
    main()
