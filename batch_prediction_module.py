# Imports the Google Cloud client library
import json
import os

import parameters
from google.cloud import storage
from upload_database import upload_local_directory_to_gcs, run_over_dir_tree_json
from load_images_gsv import runOverExel
import background_files.analyze_results as analyze_results
import shutil
import database

# Create a list of dictionaries, where each dictionary represents a data entry
test_dir = './batch'
exel_path = parameters.batch_addresses_exel
addresses, neighborhoods = runOverExel(exel_path, test_dir)

data_list = run_over_dir_tree_json(test_dir)
# Specify the file path where you want to save the JSON file
# Open the file in write mode and use json.dump() to write the data to the file
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
for i, directory in enumerate(os.listdir(test_dir)):
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
    all_final_neighborhoods.append(neighborhoods[i])


# add the final files to the database
database.add_new_prediction(all_final_results, all_final_addresses, all_final_neighborhoods)

# delete all the files (images on disc and cloud)
blobs = bucket.list_blobs(prefix=test_dir[2:])
for blob in blobs:
    blob.delete()
shutil.rmtree(test_dir)
