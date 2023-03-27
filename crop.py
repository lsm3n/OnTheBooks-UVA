import pathlib
import shutil


import cv2
import os, sys, csv
import traceback
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from scipy import stats

from PIL import Image, ImageChops, ImageStat, ImageOps, ImageFilter
import pytesseract

from crop_functions import *

def volList(volume):
    images_dir = f"images/{volume}"
    volume_path = os.path.join(os.getcwd(), images_dir)
    file_list = []

    filepaths = [f.path for f in os.scandir(volume_path) if f.is_file()]
    for filename in filepaths:
        if pathlib.Path(filename).suffix == '.jpg':
            file_list.append(filename)
    file_list.sort()
    return file_list, volume

def old_volList(volume):
    dirpath = sys.path.append(os.path.abspath("./"))
    os.chdir('images/'+str(volume))

    content = os.listdir(dirpath)
    content = [x for x in os.listdir(dirpath) if '.jpg' in x]

    iter_len = len(content)
    list = []
    for e in range(iter_len):
        f = os.path.join(os.getcwd(), content[e])
        list.append(f)
    return list, volume

def croptest(path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    for i, path in enumerate(path_list):
        filename = os.path.basename(path)
    print(filename)
    img = cv2.imread(path)
    contours, hierarchy = get_contours(img, dil_iter)

    plt.imshow(img)
    plt.show()


def oldcrop(path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    imgs_dict = {}
    imgs_df = pd.DataFrame(columns=["id", "path", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    y1 = y2 = x1 = x2 = 0

    for i, path in enumerate(path_list):
        error = False

        img = cv2.imread(path)
        filename = os.path.basename(path)
        contours, hierarchy = get_contours(img, dil_iter)
        c_df = contour_df(img, contours, hierarchy)

        try:
            x1, x2, y1, y2 = main_bbox(img, c_df, x_buffer, y_buffer)
        except:
            print(f"There was an issue finding the main bounding box with {path}")
            print(f"{path} looks like this:")
            error = True

        cropped = img[y1:y2, x1:x2]
        check = check_for_marginalia(cropped)

        if check == True:
            try:
                diff = remove_child_marginalia(cropped, dil_iter)
                x1 = x1 + diff
            except:
                print(f"There was an issue removing child marginalia with {path}")
                error = True

        cropped = img[y1:y2, x1:x2]

        try:
            top_diff, bottom_diff = crop_round2(cropped, dil_iter)
            y1 = y1+top_diff
            y2 = y2 - bottom_diff
        except:
            print(f"There was an issue in the second round of cropping with {path}")
            error = True

        imgs_dict[i] = {
            'path': path,
            'filename': filename,
            'bbox_x1': x1,
            'bbox_y1': y1,
            'bbox_x2': x2,
            'bbox_y2': y2,
                }

def crop(volume, path_list, dil_iter=30, x_buffer=20, y_buffer=5):
    imgs_dict = {}
    imgs_df = pd.DataFrame(columns=["id", "path", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])
    path_list.sort()
    y1 = 0
    y2 = 0
    x1 = 0
    x2 = 0
    for i, path in enumerate(path_list):
        img = cv2.imread(path)

        filename = os.path.basename(path)
        contours, hierarchy = get_contours(img, dil_iter)

        c_df = contour_df(img, contours, hierarchy)

        error = False
        try:
            x1, x2, y1, y2 = main_bbox(img, c_df, x_buffer, y_buffer)
        except:
            print(f"There was an issue finding the main bounding box with {path}")
            print(f"{path} looks like this:")
            error = True

        cropped = img[y1:y2, x1:x2]

        check = check_for_marginalia(cropped)

        if check == True:
            try:
                diff = remove_child_marginalia(cropped, dil_iter)
                x1 = x1 + diff
            except:
                print(f"There was an issue removing child marginalia with {path}")
                error = True

        cropped = img[y1:y2, x1:x2]

        try:
            top_diff, bottom_diff = crop_round2(cropped, dil_iter)
            y1 = y1+top_diff
            y2 = y2 - bottom_diff
        except:
            print(f"There was an issue in the second round of cropping with {path}")
            error = True

        imgs_dict[i] = {
            'path': path,
            'filename': filename,
            'bbox_x1': x1,
            'bbox_y1': y1,
            'bbox_x2': x2,
            'bbox_y2': y2,
                }
        cwd = os.getcwd()

        if error is True:
            dir = f"{cwd}/images/{volume}/issues/"
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=False)
            plt.imsave(dir + filename, img)
            print('image with issues saved to issues folder')
        else:
            dir = f"{cwd}/images/{volume}/cropped/"
            if not os.path.exists(dir):
                os.makedirs(dir, exist_ok=False)
            name = filename.replace('.jpg', '')
            plt.imsave(dir + name + '_crop.jpg', img[y1:y2, x1:x2])
        dir = f"{cwd}/images/{volume}/originals/"
        if not os.path.exists(dir):
            os.makedirs(dir, exist_ok=False)
        try:
            shutil.move(filename, f"{dir}{filename}")
        except OSError:
            pass
        plt.close()



    imgs_df = pd.DataFrame(columns=["id", "path", "filename", "bbox_x1", "bbox_y1", "bbox_y1", "bbox_y2"])

    imgs_df = pd.DataFrame.from_dict(imgs_dict, orient="index")
    imgs_df.to_csv(f"./{volume}_contourreport.csv", index_label="ID")

def get_stats(volume):
    coords = ["x1", "y1", "x2", "y2"]

    dirpath = sys.path.append(os.path.abspath("./"))
    os.chdir('../images/'+str(volume))
    df = pd.read_csv(f"./{volume}_contourreport.csv")
    files = []
    for coord in coords:
        #print(np.std(df[f"bbox_{coord}"]))
        column = f"bbox_{coord}"
        z = np.abs(stats.zscore(df[column]))
        outliers = np.where(z > 2.5)
        for outlier in outliers:
            for index in outlier:
                file = df['filename'].values[index]
                print(file)
                files.append(file)
                shutil.copy("./originals/" + file, "./issues/" + file)
        df[f"bbox_{coord}_z"] = z
    df.to_csv(f"{volume}_z-scores.csv", index=False)
    return files


# based on bbx scores no additional math (ie x2-x1 for column width outlier, consi
# handedness

def process_outliers(volume):
    coords = ["x1", "x2"]
    df = pd.read_csv(f"./{volume}_contourreport.csv")
    files = []
    for coord in coords:
        #print(np.std(df[f"bbox_{coord}"]))
        column = f"bbox_{coord}"
        z = np.abs(stats.zscore(df[column]))
        outliers = np.where(z > 2.5)
        for outlier in outliers:
            for index in outlier:
                file = df['filename'].values[index]
                files.append(file)
                try:
                    shutil.copy("./originals/" + file, "./issues/" + file)
                except:
                    pass
                filename = file.replace('.jpg', '')
                target = f"./cropped/{filename}_crop.jpg"
                if os.path.exists(target):
                    os.remove(target)
                else:
                    pass

        df[f"bbox_{coord}_z"] = z
    df.to_csv(f"{volume}_z-scores.csv", index=False)
    files.sort()
    return files



def reprocess_issues(volume):
    dirpath = sys.path.append(os.path.abspath("./"))
    #os.chdir('../../images/'+str(volume)+'/issues')
    os.chdir('../../issues/')
    issues_list = os.listdir(dirpath)
    issues_list.sort()
    print(issues_list)

def volListOld(date):
    dirpath = sys.path.append(os.path.abspath("./"))
    os.chdir('../images/'+str(date))

    content = os.listdir(dirpath)
    content = [x for x in os.listdir(dirpath) if '.jpg' in x]

    iter_len = len(content)
    for e in range(iter_len):
        f = os.path.join(os.getcwd(), content[e])
        try:
            img = crop_image(f)
            path = "./cropped"
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=False)
            filename = content[e].replace('.jpg', '')

            cv2.imwrite('./cropped/'+ filename +'_crop.jpg', img)
            print('success:' + filename)
        except Exception as Argument:
            print(filename)
            traceback.print_exc()




def image_prep():
    print('deskew')






def volListOld(date):
    dirpath = sys.path.append(os.path.abspath("./"))
    os.chdir('../images/'+str(date))

    content = os.listdir(dirpath)
    content = [x for x in os.listdir(dirpath) if '.jpg' in x]

    iter_len = len(content)
    for e in range(iter_len):
        f = os.path.join(os.getcwd(), content[e])
        try:
            img = crop_image(f)
            path = "./cropped"
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=False)
            filename = content[e].replace('.jpg', '')

            cv2.imwrite('./cropped/'+ filename +'_crop.jpg', img)
            print('success:' + filename)
        except Exception as Argument:
            print(filename)
            traceback.print_exc()

def old():
    sys.path.append(os.path.abspath("./"))
    pytesseract.pytesseract.tesseract_cmd = r'/opt/homebrew/Cellar/tesseract/5.2.0/bin/tesseract'
    master = []
    with open("TEST_marginalia_metadata.csv", "r") as csvfile:
        reader = csv.DictReader(csvfile)
        print(reader)
        os.chdir('../')
        for row in reader:

            img = os.path.join("images",row["year"],row["file"])
            name = os.path.split(img)[1]
            img = Image.open(img)
            filename = row["file"].replace('.jpg', '')

            img = img.rotate(float(row["angle"]))
            img = img.crop((float(row["bbox1"]), float(row["bbox2"]), float(row["bbox3"]), float(row["bbox4"])))
            img = ImageOps.expand(img, border = 200, fill = 255)
            img.show()


            pconfig = "--psm " + str(1)
            oconfig = "--oem " + str(3)
            tconfig = pconfig + " " + oconfig

            mode = {"mode": "a"}
            #mode = {"mode": "w"}

            outdir = "output"
            savpath = os.path.normpath(os.path.join(outdir, filename + "_ocr.txt"))

            #ocrf = open(savpath, "a")
            text = pytesseract.image_to_string(img, config = tconfig)

            print(text)


            row_dict = dict()
            row_dict["filename"] = row["file"]
            row_dict["year"] = row["year"]
            row_dict["rotate"] = row["angle"]
            row_dict["left"] = row["bbox1"]
            row_dict["up"] = row["bbox2"]
            row_dict["right"] = row["bbox3"]
            row_dict["lower"] = row["bbox4"]
            row_dict["border"] = 200
            row_dict["bkgcol"] = [255, 255, 255]
            master.append(row_dict)
            cuts = {
                "rotate" : row["angle"],
                "left" : row["bbox1"],
                "up" : row["bbox2"],
                "right" : row["bbox3"],
                "lower" : row["bbox4"],
                "border" : 200
            }
            adjustments = {
                "color": "",
                "autocontrast": "",
                "blur": "",
                "sharpen": "",
                "smooth": "",
                "xsmooth": ""
            }


            #cut = cutMarg(img, **cuts)
          #  cut.show()
            """
            tsvOCR((cutMarg(img, cuts)),
                       savpath = os.chdir("data"),
                       tsvfile = filename + "_data.tsv")
            """
