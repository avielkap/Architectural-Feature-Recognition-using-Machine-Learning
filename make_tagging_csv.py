import os
import csv
import parameters
import pandas as pd

directory = parameters.untagged_photos_dir
header = ["כתובת", "קובץ"] + parameters.features
path = parameters.tagging_photos_file
def is_relevant():
    return os.path.isfile(path)

def make_csv():
    if is_relevant():
        print('adding to exiting file - '+path)
        old_data = pd.read_csv(path)
        # new columns
        old_header = old_data.head(0).columns
        new_features = set(header) - set(old_header)
        new_col_value = ['-'] * len(old_data[old_header[0]])

        add_data = {}
        for feature in new_features:
            add_data[feature] = new_col_value
        new_table = old_data.assign(**add_data)

        addresses_new = set(os.listdir(directory)) - set(old_data['כתובת'])
        for addr in addresses_new:
            f = os.path.join(directory, addr)
            for imagefile in os.listdir(f):
                if 'gsv' not in imagefile:
                    continue
                line = [addr, imagefile] + ['-'] * (len(header) - 2)
                new_table.loc[len(new_table.index)] = line

        new_table.to_csv(path, index=False)

    else:
        # add saving the previous csv
        # add checking if there is relevant csv
        print('making new file - '+path)
        row = 1
        lines = []
        for addr in os.listdir(directory):
            f = os.path.join(directory, addr)
            for imagefile in os.listdir(f):
                if 'gsv' not in imagefile:
                    continue
                line = [addr, imagefile] + ['-'] * (len(header) - 2)
                row += 1
                lines.append(line)



        with open(path, 'w', newline='', encoding='utf-8') as csv_output:
            writer = csv.writer(csv_output)
            writer.writerow(header)
            writer.writerows(lines)
