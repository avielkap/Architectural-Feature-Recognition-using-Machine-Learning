from gcloud import storage
import parameters
from background_files.convert_hebrew_to_english import convert_hebrew_to_english


def get_string_between_last_and_pre_last_slashes(input_string):
    # Find the last occurrence of '/'
    last_slash_index = input_string.rfind('/')

    # Find the pre-last occurrence of '/'
    pre_last_slash_index = input_string.rfind('/', 0, last_slash_index)

    # Check if both slashes are found
    if last_slash_index != -1 and pre_last_slash_index != -1:
        # Extract the substring between the last and pre-last slashes
        result = input_string[0:last_slash_index] + input_string[
                                                  pre_last_slash_index :last_slash_index] + '_' + input_string[
                                                                                                     last_slash_index + 1:]
        return result
    else:
        # If one or both slashes are not found, return an empty string
        return input_string


def rename_blob(bucket_name):
    """
    Function for renaming file in a bucket buckets.

    inputs
    -----
    bucket_name: name of bucket
    blob_name: str, name of file
        ex. 'data/some_location/file_name'
    new_blob_name: str, name of file in new directory in target bucket
        ex. 'data/destination/file_name'
    """
    client = storage.Client()

    bucket = client.bucket(bucket_name)
    blobs_specific = list(bucket.list_blobs(prefix=parameters.untagged_photos_dir[2:]))
    print(blobs_specific[0].name)
    for blob in blobs_specific:
        new_name = convert_hebrew_to_english(blob.name)
        new_name=get_string_between_last_and_pre_last_slashes(new_name)
        if not new_name == blob.name:
            bucket.rename_blob(blob, new_name)


rename_blob(parameters.data_bucket)
print(get_string_between_last_and_pre_last_slashes('photos/Avraham_Boyer_St_10_tl_abyb_ypv/gsv_0.jpg'))