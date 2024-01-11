import pandas as pd
import random
from gcloud import storage

import parameters
from background_files.convert_hebrew_to_english import convert_hebrew_to_english

path = parameters.tagging_photos_file

# The name for the new bucket
directory = parameters.untagged_photos_dir

base_path = 'gs://' + parameters.data_bucket + '/' + directory[2:]

# Reading blobs, parsing information and creating the csv file
filename = parameters.data_tags_csv


def find_angel(filename):
    filenum = int(filename[4])
    angel = 10 + filenum * 10
    return str(angel)


def is_valid_utf8(string):
    try:
        a = string.encode('utf-8')
        if string == a.decode():
            return True
        else:
            return False
    except UnicodeDecodeError:
        return False


def preparedata(feature):
    df = pd.read_csv(path, usecols=['קובץ', 'כתובת', feature])
    features = dict()
    weights = dict()
    if feature not in df.columns:
        print("no feature")
        return
    split = ''
    inx_row = 0
    row = df.iloc[inx_row]
    num_rows = int(len(df.index))
    with open(filename, 'w+') as f:
        while row[feature] != '-' and inx_row < num_rows:
            # split the data
            coin_value = random.uniform(0, 1)
            if coin_value < 0.8:  # train
                split = 'TRAIN'
            elif coin_value < 0.9:  # valid
                split = 'VALIDATION'
            else:  # test
                split = 'TEST'
            for i in range(parameters.photos_per_addr):
                while row[feature] not in features.keys():
                    tag = input('how to tag this category: (y/n/i) ' + row[feature] + " ")
                    if tag == 'i':
                        tag = 'ignore'
                        features[row[feature]] = tag
                    elif tag == 'y':
                        tag = 'yes'
                        features[row[feature]] = tag
                    elif tag == 'n':
                        tag = 'no'
                        features[row[feature]] = tag
                    else:
                        print('this is not one of the option.')

                tag = features[row[feature]]
                if tag == 'ignore' or ',' in row['כתובת']: # or ',' in row['כתובת']
                    inx_row += 1
                    row = df.iloc[inx_row]
                    continue
                # while row[feature] not in weights.keys():
                #     weight = input('how to weight this category: (integer between 1 - 10,000) ' + row[feature] + " ")
                #     if weight.isdigit() and 1 <= int(weight) <= 10000:
                #         weights[row[feature]] = int(weight)
                #     else:
                #         print('incorrect number')
                weight = weights[row[feature]]
                addr_bucket_path = base_path + '/' + convert_hebrew_to_english(row['כתובת'])
                file_bucket_path = addr_bucket_path + '/' + convert_hebrew_to_english(row['כתובת']) + '_' + row['קובץ']
                if not is_valid_utf8(', '.join([split, file_bucket_path, tag, str(weight)])):
                    print(file_bucket_path, ' - there is a problem')

                f.write(', '.join([split, file_bucket_path, tag]))
                f.write("\n")
                inx_row += 1
                row = df.iloc[inx_row]
    client = storage.Client()
    bucket = client.get_bucket(parameters.data_bucket)
    blob = bucket.blob(filename)
    blob.upload_from_filename(filename)


preparedata(parameters.dataset_feature)
