from crop import *
from ocr import *


def single(volume):
    list, volume = volList(volume)
    if len(list) > 0:
        crop(volume, list, 35, 20, 20)
        #outliers = process_outliers(volume)
    else:
        print('no images files in root of volume directory')

volume = '1964'
single(volume)
#list = volList(volume)
#single(list)

def crop_all_volumes():
    #dirpath = sys.path.append(os.path.abspath("./"))
    #os.chdir('../../images/')
    #volumes = os.listdir('../../images/')
    volumes.sort()
    for volume in volumes:
        if not os.path.exists(f"../../images/{volume}/cropped") and os.path.isdir(f"../../images/{volume}"):
            list, volume = volList(volume)
            crop(volume, list, 27, 20, 20)
            outliers = process_outliers(volume)
            print(volume + "done")

def ocr_all_croppped_volumes():
    volumes = os.listdir('../../images/')
    volumes.sort()
    for volume in volumes:
        if os.path.exists(f"../../images/{volume}/cropped") and os.path.isdir(f"../../images/{volume}"):
            ocr_cropped_volume(volume)

#ocr_all_croppped_volumes()
#reprocess_issues('1865-66')


