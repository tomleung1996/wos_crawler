import bibtexparser


def run():
    bibtex_filename = r'C:\Users\Tom\PycharmProjects\wos_crawler\output\advanced_query\2019-01-20-16.35.46\1-500.bib'

    with open(bibtex_filename, 'r', encoding='utf-8') as file:
        bib_db = bibtexparser.load(file)

    print(len(bib_db.entries))

if __name__ == '__main__':
    run()