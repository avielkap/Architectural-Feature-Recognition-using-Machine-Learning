# Imports the Google Cloud client library
import json
import parameters
from google.cloud import storage
from upload_database import convert_hebrew_to_english
import pandas as pd
import background_files.analyze_results as analyze_results
from sklearn import metrics
from upload_database import upload_local_directory_to_gcs

# Create a list of dictionaries, where each dictionary represents a data entry
test_dir = parameters.test_directory_name

# get the addresses and the tags
tags_path = parameters.tagging_test_photos_file
feature = parameters.model_feature
df = pd.read_csv(tags_path, usecols=['קובץ', 'כתובת', feature])


def check_addr_tag(row_inx):
    yes = 0
    ignore = 0
    for i in range(6):
        if df.iloc[row_inx + i][feature] == 'yes':
            yes += 1
        elif df.iloc[row_inx + i][feature] != 'no':
            print('please use only yes or no tags for tests')
        if yes >= parameters.minimal_yes_bar:
            return 'yes'
    return 'no'


def get_tags():
    if parameters.model_feature not in df.columns:
        print("no feature")
        return
    inx_row = 0
    addresses_list = []
    tags = []
    num_rows = int(len(df.index))
    for inx_addr in range(0, num_rows, parameters.photos_per_addr):
        row = df.iloc[inx_addr]
        if row[feature] == '-':
            # address = row['כתובת']
            # max_idx=addresses_list.index(address)
            # addresses_list=addresses_list[max_idx]
            break
        address = row['כתובת']
        addresses_list += [address]
        tags.append(check_addr_tag(inx_addr))
    return addresses_list, tags


addresses, real_tags = get_tags()

assert len(addresses) == len(real_tags)


def get_json():
    data_list = []
    base_path = 'gs://' + parameters.batch_bucket

    num_rows = int(len(df.index))
    for inx_row in range(num_rows):
        row = df.iloc[inx_row]
        if row[feature] == '-':
            break
        if row['כתובת'] not in addresses:
            continue
        path = convert_hebrew_to_english(
            base_path + '/' + test_dir[2:] + '/' + row['כתובת'] + '/' + row['כתובת'] + '_' + row['קובץ'])
        data_list.append({"content": path, "mimeType": "image/jpeg"})
    return data_list


data_list = get_json()
# Specify the file path where you want to save the JSON file
# Open the file in write mode and use json.dump() to write the data to the file
assert len(addresses) * 6 == len(data_list)
filename = parameters.batch_json

# upload the json and test directory to the cloud
client = storage.Client()
bucket = client.get_bucket(parameters.batch_bucket)
upload_local_directory_to_gcs(test_dir, bucket)

blob = bucket.blob(filename[2:])

# rusult filename parameter

result_filename = 'prediction_results/last_prediction.jsonl'

# run over the addresses and make batch for each of them
all_final_results = []  # all the variables that will send to database.add_prediction
all_final_addresses = []
all_final_neighborhoods = []
for i, directory in enumerate(addresses):
    # write to json
    print("check address ", directory)
    with open(filename, 'w') as input_json:
        for entry in data_list[i * parameters.photos_per_addr: (i + 1) * parameters.photos_per_addr]:  # take the -
            # - relevant part
            json.dump(entry, input_json)
            input_json.write('\n')
    blob.upload_from_filename(filename[2:])
    # make batch
    batch_prediction_job = analyze_results.make_batch(filename[2:])
    print("got results for address ", directory)
    # download the results file
    results_folder = batch_prediction_job.output_info.gcs_output_directory
    blob = bucket.blob(results_folder[len('gs://' + parameters.batch_bucket) + 1:] + '/predictions_00001.jsonl')
    blob.download_to_filename(result_filename)
    # read the results
    results = []
    with open(result_filename, "r") as file:
        for line in file:
            data = json.loads(line)
            results.append(data)
    # check we got all the answers
    if len(results) != parameters.photos_per_addr:
        print('problem :not all the results came back')
        continue
    # add to the final files
    all_final_results += results
    all_final_addresses.append(directory)


# analyze the results
def get_prediction(prediction_results, addresses_list):
    tags = []
    for i_addr, addr in enumerate(addresses_list):
        yes_confidence = []
        for i in range(parameters.photos_per_addr):
            pred = prediction_results[i_addr * parameters.photos_per_addr + i]['prediction']
            if pred['displayNames'][0] == 'yes':
                yes_confidence.append(pred['confidences'][0])
            else:
                yes_confidence.append(pred['confidences'][1])
        yes_num = sum(i > parameters.confidence_bar_for_yes for i in yes_confidence)
        final_res = 'no'
        if yes_num >= parameters.minimal_yes_bar:
            final_res = 'yes'
        print(addr + ' is tagged as ' + final_res)
        tags.append(final_res)
    return tags


processed_final_results = get_prediction(all_final_results, all_final_addresses)

# print final results

print(metrics.confusion_matrix(real_tags, processed_final_results))
print(metrics.classification_report(real_tags, processed_final_results,
                                    target_names=['yes', 'no']))
