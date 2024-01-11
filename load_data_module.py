import load_images_gsv
import upload_database
import parameters
from google.cloud import storage
import make_tagging_csv

load_images_gsv.runOverExel(parameters.address_list, parameters.untagged_photos_dir)
client = storage.Client()
bucket = client.get_bucket(parameters.data_bucket)
upload_database.upload_local_directory_to_gcs(parameters.untagged_photos_dir, bucket)
make_tagging_csv.make_csv()
