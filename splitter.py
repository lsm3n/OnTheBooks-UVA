import csv
import os
import nltk
import pandas as pd



def get_text():
    lawlist = f"{os.getcwd()}/data/identified_laws.csv"
    index_array = []
    with open(lawlist, encoding='utf-8-sig', newline='') as csv_file:
        reader = csv.DictReader(csv_file)
        keyed_arrays = []

        for row in reader:
            keyed_array = {}
            for header, value in row.items():
                keyed_array[header] = value
            keyed_arrays.append(keyed_array)

    return keyed_arrays

def last8(x):
    start = x.index("law") + len("law")
    end = x.index(".", start)
    return int(x[start:end])


def tokenize_corpus():
    volumes = f"{os.getcwd()}/images/"
    volumes = [file for file in os.listdir(volumes) if os.path.isdir(os.path.join(volumes, file))]
    sid = 0
    corpus_sentences = []
    for volume in sorted(volumes):
        laws_dir = f"{os.getcwd()}/images/{volume}/laws"
        files = os.listdir(laws_dir)
        filtered = [item for item in files if not item.startswith('preceedingmaterials')]

        for filename in sorted(filtered, key=last8):
            if not filename.startswith("preceeding"):
                start = filename.index("law") + len("law")
                end = filename.index(".", start)
                lawnumber = int(filename[start:end])
                file_url = f"{laws_dir}/{filename}"

                if os.path.exists(file_url):
                    with open(file_url, 'r') as file:
                        text = file.read()
                        text = text.replace('\n', ' ')
                        tokenizer = nltk.tokenize.PunktSentenceTokenizer()
                        sentences = tokenizer.sentences_from_text(text)
                        for sentence in sentences:
                            sid += 1
                            data = [filename, volume, lawnumber, sid, sentence]
                            corpus_sentences.append(data)
    laws_data = pd.DataFrame(corpus_sentences, columns=['Filename', 'Volume', 'Law Number', 'SID', 'Sentence'])


    #pd.set_option('display.max_columns', None)
    #print(laws_data)

    laws_data.to_csv(f"{os.getcwd()}/data/corpus_sentences.csv")



def iterator():


    data = get_text()
    for row in data:

        file_path = f"{os.getcwd()}/images/{row['Volume']}/laws/VAactsofassembly_{row['Volume']}_law{row['Chapter']}.txt"
        output_path = f"{os.getcwd()}/data/exploded/VAactsofassembly_{row['Volume']}_law{row['Chapter']}_exploded.csv"

        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                text = file.read()
                text = text.replace('\n', '')
                sentences = text.split('. ')

                with open(output_path, 'w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['phrase'])
                    for sentence in sentences:
                        writer.writerow([sentence])

        else:
            print(f"The file {os.path.basename(file_path)} does not exist.")





def split_text(volume):
    laws_dir = f"{os.getcwd()}/images/{volume}/laws"
    volume_dir = f"{os.getcwd()}/images/{volume}"
    files = os.listdir(laws_dir)

    laws = []
    for file in files:
        print(file)
        para = []
        data = []
        path = f"{laws_dir}/{file}"
        if pathlib.Path(file).suffix == '.txt':
            with open(path) as infile:
                for line in infile:
                    cleaned = line.rstrip('\n')
                    if cleaned != '':
                        para.append(cleaned)
                    if cleaned == '':
                        break
        para = ' '.join(para)

        #if int(volume) > 1949:
            #pattern = re.compile(r"CHAPTER\s*(\d+)\s*\n", re.IGNORECASE)
        #else:
        pattern = re.compile(r"Chap\. \d+(\,|\.)", re.IGNORECASE)


        lawmatch = pattern.search(para)
        if lawmatch:
            numberpattern = re.compile(r'\d+')
            numbermatch = numberpattern.search(lawmatch.group())
            lawnumber = numbermatch.group()
            posend = numbermatch.end()
        if posend:
            title = para[posend+2:]
        else:
            title = para
        data = [lawnumber, title]
        laws.append(data)


    laws_data = pd.DataFrame(laws, columns=['Law Number', 'Law Title'])
    laws_data.sort_values(by='Law Number')
    laws_data.to_csv(f"{volume_dir}/{volume}_lawtitles.csv")
