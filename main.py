from indexer import Indexer


def main():
    for dataset_name in ["yelp", "headlines"]:
        dataset_path = f"./sample_data/{dataset_name}.txt"
        parser = Indexer(dataset_path, dataset_name)

        parser.calculate_metrics()
        parser.find_singleton_words()
        parser.find_frequencies()


if __name__ == '__main__':
    main()
