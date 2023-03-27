import sys, os
import pandas as pd




def volume_data(volume):
    cwd = os.getcwd()

    pages = [x for x in os.listdir(f"{cwd}/images/{volume}/originals") if '.jpg' in x]
    cropped = [x for x in os.listdir(f"{cwd}/images/{volume}/cropped") if '.jpg' in x]
    issues_dir = f"{cwd}/images/{volume}/issues"
    if os.path.exists(issues_dir):
        issues = len([x for x in os.listdir(issues_dir) if '.jpg' in x])
    else:
        issues = "None"
    if(len(pages) > 0):
        percent = len(cropped) / len(pages)
        progress = f"{percent:.1%}"
        pages = len(pages)
    else:
        pages = "n/a"
        progress = "n/a"

    return pages, progress, issues


def prepare_report():
    cwd = os.getcwd()
    dir = f"{cwd}/images"
    volumes = os.listdir(dir)
    volumes.sort()
    report = pd.DataFrame(columns=["volume", "pages", "percent_cropped", "issues"])
    stats_dict = {}
    for i, volume in enumerate(volumes):
        dir = f"{cwd}/images/{volume}"
        if os.path.exists(f"{cwd}/images/{volume}/cropped") and os.path.isdir(f"{cwd}/images/{volume}"):

            pages, progress, issues = volume_data(volume)
            stats_dict[i] = {
                'volume': volume,
                'pages': pages,
                'percent_cropped': progress,
                'issues': issues,
                }
        else:
            if os.path.isdir(f"{cwd}/{volume}"):
                stats_dict[i] = {
                    'volume': volume,
                    'pages': "unprocessed",
                    'percent_cropped': "unprocessed",
                    'issues': "unprocessed",
                    }
    report = pd.DataFrame.from_dict(stats_dict, orient="index")
    print(report.to_string())




#get_volumes()
prepare_report()
