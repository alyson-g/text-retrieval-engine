from parser import Parser


def main():
    for dataset_name in ["yelp", "headlines"]:
        document_path = f"./sample_data/{dataset_name}.txt"
        parser = Parser(document_path, dataset_name)

        parser.calculate_metrics()
        parser.find_singleton_words()
        parser.find_frequencies()


if __name__ == '__main__':
    main()
