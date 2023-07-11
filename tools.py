import json
import re

import shutil
import sys, os, pathlib
import glob
import datetime
import numpy as np
import pandas as pd
import csv

volume = '1865es'


def compile_flagged_laws(volume, lawnumber):
    cwd = os.getcwd()
    path = f"{cwd}/images/{volume}/laws/VAactsofassembly_{volume}_law{lawnumber}.txt"
    lines = []
    with open(path, 'r', encoding="utf-8") as file:
        for line in file:
            # Remove hyphens at end of line
            line = line.rstrip('-')
            # Remove line breaks
            line = line.replace('\n', ' ')
            # Add line to list
            lines.append(line)
        # Join lines into a single string
        text = ' '.join(lines)
        # Split text at every period
        sentences = text.split('. ')
        # Create DataFrame from list of sentences
        df = pd.DataFrame(sentences, columns=['Sentence'])

    save = f"{cwd}/flagged/VAacts_exploded_{volume}_law{lawnumber}.csv"
    df.to_csv(save, index=False, encoding="utf-8")


def merge_txt_save(volume):
    cwd = os.getcwd()
    dir = f"{cwd}/images/{volume}/text/"
    read_files = glob.glob("*.txt")
    read_files.sort()
    with open(f"merged_{volume}.txt", "wb") as outfile:
        for f in read_files:
            with open(f, "rb") as infile:
                outfile.write(infile.read())

def gather_laws():
    cwd = os.getcwd()
    search = f"{cwd}/images/**/laws/*.txt"
    files = glob.glob(search, recursive=True)

    csv_path = f"{cwd}/aggregate_laws.csv"

    data = []
    fields = ['filename', 'volume', 'lawnumber', 'lawtext']

    # Save the DataFrame to a CSV file, encoded as UTF-8

    for file in files:
        filename = os.path.basename(file)
        if not filename.startswith("preceeding"):
            #extract volume from filename of laws, igoring content before first law in volume
            start = filename.index("_") + 1
            end = filename.index("_", start)
            volume = filename[start:end]

            #extract law number
            start = filename.index("law") + len("law")
            end = filename.index(".", start)
            lawnumber = int(filename[start:end])
            #data.append({"filename": filename, "volume": volume, "lawnumber": lawnumber})
            #data.append({filename, volume, lawnumber})
            with open(file, 'r', encoding="utf-8") as law:
                lawtext = law.read()

               # lawtext = ""
                data.append({"filename": filename, "volume": volume, "lawnumber": lawnumber, "lawtext": lawtext})


    sorted_data = sorted(data, key=lambda x: (x['volume'], x['lawnumber']))
    df = pd.DataFrame(sorted_data, columns=fields)

    df.to_csv(csv_path, index=False, encoding="utf-8")



def gather_texts():
    cwd = os.getcwd()
    search = f"{cwd}/images/**/*.txt"
    files = glob.glob(search, recursive=True)
    current_time = datetime.datetime.now()
    date = datetime.date.today()
    time = f"{current_time.hour}-{current_time.minute}"
    dt = f"{date}_{time}"
    cwd = os.getcwd()
    ocr_dir = f"{cwd}/ocr/"
    if not os.path.exists(ocr_dir):
        os.mkdir(ocr_dir)
    dir = f"{ocr_dir}/aggocr_{dt}"
    os.mkdir(dir)

    for file in files:
        filename = os.path.basename(file)
        shutil.copy(file, f"{dir}/{filename}")





def clean(volume):
    docs = os.chdir(f'../../images/{volume}/text')
    read_files = glob.glob("*.txt")
    read_files.sort()

    for f in read_files:
        text = open(f, 'rb')
        print(text)





def qc_regex():
    chap_law_header = ['Ciap.', 'Oxnap.', 'Oxap.', 'Cuar.', 'Cap.', 'CHuap.', 'Cuap.', 'Chapr.', 'CHar.', 'CuHap.', 'CuaPp.',
                       'CHap.', 'CuHap.', 'Crap.', 'CuHapP.', 'Coap.', 'Omar.', 'Cap,', 'Cuap,', "Caap.", "Cap."
                       'Cuaar.', 'Cxap.', 'Onap.', 'Caar.', 'Cuaap.', 'Cgap.', 'Cwap.', 'Caap,', 'Ouap.', 'Cuapr.',
                       'Oar.', 'Hap.', 'Crap.', 'Crap,', 'Cuav.', 'Cnap.']
    page_header_check = 'YYYY ACTS OF ASSEMBLY XX'
    return chap_law_header


def qc_process(volume = False):
    target_dir = f"{os.getcwd()}/process"
    if volume:
        target_dir = f"{os.getcwd()}/images/{volume}/text"
    files = os.listdir(target_dir)
    lines = []
    for file in files:
        print(file)
        path = f"{target_dir}/{file}"
        if pathlib.Path(file).suffix == '.txt':
            with open(path) as infile:
                for line in infile:
                    for pattern in qc_regex():
                        line = line.replace(pattern, "Chap.")
                    lines.append(line)
            with open(path, 'w') as outfile:
                for line in lines:
                    outfile.write(line)
        lines = []
    print("Processed OCR Corrections")

def comp_issues():
    volumes = os.listdir('../../images/')
    volumes.sort()
    issues = []
    if not os.path.exists("../../issues"):
        os.makedirs("../../issues", exist_ok=False)
    for volume in volumes:
        if os.path.exists(f"../../images/{volume}/issues"):
            directory = f"../../images/{volume}/issues"
            for file in os.listdir(directory):
                filepath = os.path.join(directory, file)
                #issues.append(filepath)
                shutil.copy(filepath, f"../../issues/{file}")

def break_laws(volume):
    text_dir = f"{os.getcwd()}/images/{volume}/text"
    target_dir = f"{os.getcwd()}/images/{volume}/laws"
    volume_dir = f"{os.getcwd()}/images/{volume}"
    if not os.path.exists(target_dir):
        os.mkdir(target_dir)
    files = os.listdir(text_dir)
    files.sort()

    data = {}
    i = 0
    lawnumber = "preceeding"
    target = f"{target_dir}/preceedingmaterials_{volume}.txt"
    data = []
    numbermatch = False
    for file in files:
        path = f"{text_dir}/{file}"
        pageid = os.path.basename(file).split('.')[0]
        new = True
        i = 1

        if pathlib.Path(file).suffix == '.txt':

            with open(path) as infile:
                #initial document to record lines preceeding first law, including frontmatter


                for line in infile:
                    #if int(volume) < 1950:
                        # pattern match for pre-1950 volumes using phrase  "Chap. ##."
                    #pattern = re.compile(r"Chap\. \d+(\,|\.)", re.IGNORECASE)
                    #else:
                        # pattern match for post-1950 volumes using phrase  "CHAPTER. ##."
                    pattern = re.compile(r"CHAPTER\s*(\d+)\s*\n")

                    lawmatch = pattern.search(line)
                    if lawmatch:
                        numberpattern = re.compile(r'\d+')
                        numbermatch = numberpattern.search(lawmatch.group())
                        lawnumber = numbermatch.group()
                        filename = f"VAactsofassembly_{volume}_law{lawnumber}.txt"
                        target = f"{target_dir}/{filename}"
                        data.append([pageid, lawnumber])
                    else:
                        if new:
                            data.append([pageid, lawnumber])
                    new = False
                    i += 1
                    law = open(target, mode='a')
                    law.write(line)
                    law.close()
    laws_data = pd.DataFrame(data, columns=['Page', 'Law Number'])
    laws_data.to_csv(f"{volume_dir}/{volume}_lawpages.csv")
    print("Processed Laws")

def extract_titles(volume):
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

        #else:
        #pattern = re.compile(r"CHAPTER\s*(\d+)\s*\n")
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




#gather_laws()


qc_process(volume)
break_laws(volume)
extract_titles(volume)
