import parameters
# from google.cloud import storage
import os
from background_files.convert_hebrew_to_english import convert_hebrew_to_english


def get_part_after_last_slash(input_string):
    # Find the last occurrence of '/'
    last_slash_index = input_string.rfind('/')

    # Check if '/' is found in the string
    if last_slash_index != -1:
        # Extract the substring after the last '/'
        result = input_string[last_slash_index + 1:]
        return result
    else:
        # If '/' is not found, return the original string
        return input_string


def upload_local_directory_to_gcs_recursive(local_path, bucket, gcs_path):
    print('uploading ' + local_path + ' to bucket')
    assert os.path.isdir(local_path)
    for local_file in os.listdir(local_path):
        if os.path.isdir(os.path.join(local_path, local_file)):
            upload_local_directory_to_gcs_recursive(os.path.join(local_path, local_file), bucket,
                                                    gcs_path + '/' + local_file)
        else:
            if 'gsv' not in local_file:
                continue
            path = gcs_path + '/' + get_part_after_last_slash(gcs_path) + '_' + local_file
            path = convert_hebrew_to_english(path)
            blob = bucket.blob(path)
            if not blob.exists():
                blob.upload_from_filename(os.path.join(local_path[2:], local_file).replace('\\', '/'))


def upload_local_directory_to_gcs(local_path, bucket):
    upload_local_directory_to_gcs_recursive(local_path, bucket, local_path[2:])


base_path = 'gs://' + parameters.batch_bucket

data_list=[]
def run_over_dir_tree_json_recursion(cur_dir):
    assert os.path.isdir(cur_dir)
    for subdir in os.listdir(cur_dir):
        if os.path.isdir(os.path.join(cur_dir, subdir)):
            run_over_dir_tree_json(cur_dir + '/' + subdir)
        else:
            if 'gsv' not in subdir:
                continue
            path = convert_hebrew_to_english(
                base_path + '/' + cur_dir[2:] + '/' + get_part_after_last_slash(cur_dir) + '_' + subdir)
            data_list.append({"content": path, "mimeType": "image/jpeg"})
    return data_list


def run_over_dir_tree_json(cur_dir):
    run_over_dir_tree_json_recursion(cur_dir)
    return data_list
# client = storage.Client()
# bucket = client.get_bucket(parameters.data_bucket)
# upload_local_directory_to_gcs('./Shlomo Ben Yosef St 7 תל אביב יפו', bucket)
