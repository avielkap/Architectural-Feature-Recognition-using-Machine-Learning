import pickle
import pandas as pd
from pandas import DataFrame as df

import parameters

databaes_columns = ['neighborhood', 'address', 'final prediction'] + ['c' + str(i) for i in
                                                                      range(parameters.photos_per_addr)] \
                   + ['feature', 'model id']


def add_new_prediction(prediction_results, addresses_list, neighborhoods):
    old_data = pd.read_csv(parameters.dataframe_path)  # encoding='cp424' hebrew
    with open(parameters.dictionary_path, 'rb') as f:
        nbhd_dict = pickle.load(f)
    with open(parameters.list_path, 'rb') as f:
        nbhd_list = pickle.load(f)
    offset = len(old_data.index)
    rows = df(columns=databaes_columns)
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
        if float(yes_num)/parameters.photos_per_addr >= parameters.minimal_yes_bar:
            final_res = 'yes'
        print(addr + ' is tagged as ' + final_res)
        row = [neighborhoods[i_addr], addr, final_res] + yes_confidence + [parameters.model_feature,
                                                                           str(parameters.model_id)]
        rows.loc[len(rows.index) + offset] = row
        if (neighborhoods[i_addr], parameters.model_feature) in nbhd_dict.keys():
            nbhd_dict[(neighborhoods[i_addr], parameters.model_feature)].append(len(rows.index) + offset - 1)
        else:
            nbhd_dict[(neighborhoods[i_addr], parameters.model_feature)] = [len(rows.index) + offset - 1]

        if neighborhoods[i_addr] not in nbhd_list:
            nbhd_list.append(neighborhoods[i_addr])
    with open('prediction_data/NBHD_dict.pkl', 'wb') as f:
        pickle.dump(nbhd_dict, f)
    with open('prediction_data/NBHD_list.pkl', 'wb') as f:
        pickle.dump(nbhd_list, f)
    old_data = pd.concat([old_data, rows], ignore_index=True, sort=False)
    old_data.to_csv(parameters.dataframe_path, index=False)
    return rows['final prediction']


def get_nf_rows(neighborhood, feature):
    data = pd.read_csv(parameters.dataframe_path)
    data['model id'] = data['model id'].astype(str)
    with open(parameters.dictionary_path, 'rb') as f:
        nbhd_dict = pickle.load(f)
    if (neighborhood, feature) not in nbhd_dict.keys():
        return None
    wanted_rows = nbhd_dict[(neighborhood, feature)]
    relevant_data = data.iloc[wanted_rows]
    return relevant_data


def get_neighborhood_rows(neighborhood):
    data = pd.read_csv(parameters.dataframe_path)
    data['model id'] = data['model id'].astype(str)
    with open(parameters.dictionary_path, 'rb') as f:
        nbhd_dict = pickle.load(f)
    wanted_rows = []
    for feature in parameters.features:
        if (neighborhood, feature) not in nbhd_dict.keys():
            continue
        feature_rows = nbhd_dict[(neighborhood, feature)]
        wanted_rows += feature_rows
    relevant_data = data.iloc[wanted_rows]
    return relevant_data


def get_neighborhoods_list():
    with open(parameters.list_path, 'rb') as f:
        nbhd_list = pickle.load(f)
    return nbhd_list


def clear_all():  # debugging function
    nbhd_dict = dict()
    with open('prediction_data/NBHD_dict.pkl', 'wb') as f:
        pickle.dump(nbhd_dict, f)
    nbhd_list = []
    with open('prediction_data/NBHD_list.pkl', 'wb') as f:
        pickle.dump(nbhd_list, f)
    clear_df = df(columns=databaes_columns)
    clear_df.to_csv(parameters.dataframe_path, index=False)


