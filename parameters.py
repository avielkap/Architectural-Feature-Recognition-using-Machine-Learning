# prepare data part - bot part
features = ["Villa on the Roof", "Frames", "Over 4 Stories", "Parasite", "3D Façade", "Color", "Balconies",
            "Hard Cladding"]
tagging_option = {'כן': 'yes', 'לא': 'no', 'התעלם': 'ignore'} #, 'מרפסת': 'balcony'
# keys = the buttom values, what the tagger see in the bot.
# values = the table values, what is written in the bot. it's better to make it in english because the computer (at list my) isn't showing it properly in hebrew.
photos_per_addr = 6
bot_id=""
# files and directories

untagged_photos_dir = './photos'
tagging_photos_file = 'csv_files/' + untagged_photos_dir[2:] + '_תיוג_תמונות.csv'
address_list = 'רשימת כתובות לבדיקה.xlsx'

dataset_feature = "Over 4 Stories"
assert dataset_feature in features
# vertex AI model part
project = "67105736832"
location = "europe-west4"
model_id = '7992099333652611072'
data_bucket = 'cloud-ai-platform-80daa6af-0f89-49f5-bc66-be6b6bd157b1'
data_tags_csv = 'csv_files/labels_csv_python.csv'
model_feature = "Balconies"

# batch prediction
batch_bucket = 'cloud-ai-platform-80daa6af-0f89-49f5-bc66-be6b6bd157b1'
batch_json = './batch_prediction/batch_prediction.jsonl'
batch_addresses_exel = 'רשימת כתובות לבדיקה.xlsx'
confidence_bar_for_yes = 0.6
minimal_yes_bar = 2 / 6

# test the model
test_directory_name = './test1'
tagging_test_photos_file = 'csv_files/' + test_directory_name[2:] + '_תיוג_תמונות.csv'

# the final predictions database
dataframe_path = './prediction_data/prediction_database.csv'
dictionary_path = './prediction_data/NBHD_dict.pkl'
list_path = './prediction_data/NBHD_list.pkl'
result_csv = './prediction_data/תוצאות השכונה.xlsx'
