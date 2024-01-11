import pandas as pd
import telebot  # telebot
from telebot import custom_filters
from telebot.handler_backends import State, StatesGroup  # States
from telebot import types
# States storage
from telebot.storage import StateMemoryStorage
import os
from telebot.types import InputMediaPhoto
import parameters
import database

# Now, you can pass storage to bot.
state_storage = StateMemoryStorage()  # you can init here another storage

bot = telebot.TeleBot(parameters.bot_id, state_storage=state_storage)


# States group.
class MyStates(StatesGroup):
    # Just name variables differently
    feature_choice = State()  # creating instances of State class is enough from now
    action_choice = State()
    tagging = State()
    one_tagging = State()
    address_tagging = State()
    check_tagging = State()
    jump_to_row = State()
    choose_data_nbrh = State()
    choose_data_feature = State()


free_features = [-1]
pics_per_addr = parameters.photos_per_addr
filename = parameters.tagging_photos_file
rows = dict()
features = dict()
assert 'csv' in filename
global file
global header


@bot.message_handler(commands=['start'])
def start(message):
    print('user is ', message.from_user.first_name, message.from_user.last_name)
    id = message.from_user.id
    bot.set_state(id, MyStates.feature_choice, message.chat.id)

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('view predicted data')
    for feature in header[2:]:
        markup.add(feature)
    bot.send_message(message.chat.id, 'choose what feature do you want to tag:', reply_markup=markup)


# csv file part


def first_run():
    path = filename
    global file
    file = pd.read_csv(path)
    global header
    header = file.head(0).columns
    global free_features
    free_features = [True] * (len(header[2:]))


first_run()


@bot.message_handler(state="*", commands=['save_and_exit'])
def cancel(message):
    global one_tag_index
    if one_tag_index != 0:
        bot.send_message(message.chat.id, 'please finish the tagging of this address first')
        return
    print('cancel -', message.from_user.first_name, message.from_user.last_name)
    id = message.from_user.id

    bot.delete_state(id, message.chat.id)
    save(message)
    if id in rows:
        del rows[id]
    if id in features:
        free_features[header.get_loc(features[id]) - 2] = True
        del features[id]
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('/start')
    bot.send_message(message.chat.id, 'click /start to re-start the bot', reply_markup=markup)


@bot.message_handler(state="*", commands=['save'])
def save(message):
    file.to_csv(filename, index=False)
    print('saved')
    bot.send_message(message.chat.id, "the file is saved")


# actions implementations part
@bot.message_handler(state=MyStates.feature_choice)
def get_feature(message):
    print('feature state')
    id = message.from_user.id
    if message.text == 'view predicted data':
        bot.set_state(id, MyStates.choose_data_feature, message.chat.id)
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add('all')
        for feature in header[2:]:
            markup.add(feature)
        bot.send_message(message.chat.id, 'choose what feature data you want to vies:', reply_markup=markup)
        return
    if not free_features[header.get_loc(message.text) - 2]:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for feature in header[2:]:
            markup.add(feature)
        bot.send_message(message.chat.id, "someone is working on this feature. choose another", reply_markup=markup)
        return
    features[id] = message.text
    free_features[header.get_loc(features[id]) - 2] = False
    bot.set_state(id, MyStates.action_choice, message.chat.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    info = types.KeyboardButton('show information')
    tag = types.KeyboardButton('start tagging')
    check = types.KeyboardButton('check tags')
    jump = types.KeyboardButton('jump to address')
    markup.add(info, tag)
    markup.add(check, jump)
    bot.send_message(message.chat.id, 'choose what do you want do to', reply_markup=markup)


def print_info(id):
    global file
    info = [0] * len(parameters.tagging_option.values())
    ignore = 0
    not_tagged = 0
    for i in range(rows[id]):
        line = file[features[id]][i]
        if line == 'ignore':
            ignore += 1
        elif line == '-':
            not_tagged += 1
        else:
            info[list(parameters.tagging_option.values()).index(line)] += 1

    no_data = len(file.index) - rows[id]
    images_num = len(file.index)
    print(images_num, no_data, ignore)
    print(info)
    message = format((images_num - no_data - not_tagged) / images_num,
                     ".0%") + " of the images are tagged, " + str(
        images_num - no_data - not_tagged) + " in total.\n" + format(
        ignore / images_num, ".0%") + " of the images are ignored.\n"
    message2 = ''
    if sum(info) > 0:
        for i in range(len(info)):
            if list(parameters.tagging_option.values())[i] != 'ignore':
                message2 += format(info[i] / sum(info), ".0%") + " of the valid images are tagged as " + \
                            list(parameters.tagging_option.values())[i] + ", "
        message2 = message2[:len(message2) - 2:]  # delete the last ", "

    else:
        message2 = 'there are no valid tagged images at all, '
    if not_tagged > 0:
        message2 += '\nthere are ' + str(not_tagged) + ' photos that not tagged at the tagged area. please re-check ' \
                                                       'the data '
    bot.send_message(id, message + message2)


def find_row(feature, id):
    # binary search
    min_lim = 0
    max_lim = int(len(file.index))
    if file[feature][min_lim] == '-':  # nothing is tagged
        rows[id] = 0
        return

    elif file[feature][max_lim - 1] != '-':  # everything is tagged
        rows[id] = max_lim
        return
    row = (min_lim + max_lim) / 2
    while not (file[feature][row] != '-' and file[feature][row + pics_per_addr] == '-'):
        if file[feature][row] == '-':
            max_lim = row
        else:
            min_lim = row
        row = int((min_lim + max_lim) / 2)
    row -= row % pics_per_addr
    rows[id] = row + pics_per_addr


@bot.message_handler(state=MyStates.action_choice)
def get_action(message):
    print('action state')
    id = message.from_user.id
    if message.text == 'show information':
        find_row(features[id], id)
        print_info(id)
    elif message.text == 'start tagging':
        find_row(features[id], id)
        if check_rows(message):
            return
        send_pics(file['כתובת'][rows[id]], message.chat.id)
        bot.set_state(id, MyStates.tagging, message.chat.id)
        bot.send_message(message.chat.id, "do you see the feature in the pics? \nthe address is " + file['כתובת'][
            rows[id]], reply_markup=markup_tagging)

    elif message.text == 'check tags':
        bot.set_state(id, MyStates.check_tagging, message.chat.id)
        rows[id] = 0
        send_pics(file['כתובת'][rows[id]], message.chat.id)
        bot.send_message(id, "this image is tagged as " + see_tag(id) + "\nthe address is " + file['כתובת'][rows[id]],
                         reply_markup=check_markup)
    elif message.text == 'jump to address':
        find_row(features[id], id)
        bot.set_state(id, MyStates.jump_to_row, message.chat.id)
        bot.send_message(id, "what address index do you want to jump? please write the number",
                         reply_markup=types.ReplyKeyboardRemove())
    elif message.text == 'run model':
        bot.send_message(id, 'maybe later')


# jumping part
@bot.message_handler(state=MyStates.jump_to_row)
def jump(message):
    print('jump state')
    id = message.from_user.id
    if not message.text[0:].isdigit():
        bot.send_message(id, "please write a number, not text")
        return
    value = int(message.text)
    row_value = (value - 1) * pics_per_addr
    if 0 <= row_value < rows[id]:
        print('jumped to ', row_value)
        rows[id] = row_value
        bot.set_state(id, MyStates.check_tagging, message.chat.id)
        send_pics(file['כתובת'][rows[id]], message.chat.id)
        bot.send_message(id, "this image is tagged as " + see_tag(id) + "\nthe address is " + file['כתובת'][rows[id]],
                         reply_markup=check_markup)
    elif rows[id] <= row_value < int(len(file.index)):
        bot.send_message(id, "you can jump only to tagged addresses, for checking them. please write another number")
    else:
        bot.send_message(id, "the number is beyond the amount of addresses/0, please write legal number")


# address - tagging part
def send_pics(addr, id):
    directory = parameters.untagged_photos_dir
    f = os.path.join(directory, addr)
    all_photos = []
    for imagefile in os.listdir(f):
        path = os.path.join(f, imagefile)
        if 'gsv' not in imagefile:
            continue
        photo = open(path, 'rb')
        mediaPhoto = InputMediaPhoto(photo)
        all_photos.append(mediaPhoto)
    if len(all_photos) > 10:
        chunks = [all_photos[x:x + 10] for x in range(0, len(all_photos), 10)]
        for c in chunks:
            bot.send_media_group(id, c)
    else:
        bot.send_media_group(id, all_photos)


def make_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for name in parameters.tagging_option.keys():
        buttons.append(types.KeyboardButton(name))
    mod = len(buttons) % 3
    for i in range(0, len(buttons) - mod, 3):
        markup.add(buttons[i], buttons[i + 1], buttons[i + 2])
    if mod == 1:
        markup.add(buttons[len(buttons) - 1])
    elif mod == 2:
        markup.add(buttons[len(buttons) - 2], buttons[len(buttons) - 1])

    # dismiss = types.KeyboardButton('התעלם')
    # markup.add(buttons)
    return markup


markup_tagging = make_markup()
markup_tagging.add('אחר')


def update_addr_csv(value, id):
    for i in range(6):
        file[features[id]][rows[id] + i] = value


def check_rows(message):
    if rows[message.from_user.id] >= int(len(file.index)):
        bot.send_message(message.from_user.id, "you tagged all the photos. very good!")
        cancel(message)
        return True
    return False


@bot.message_handler(state=MyStates.tagging)
def tagging(message):
    print('tagging state')

    inp = message.text
    id = message.from_user.id
    if inp == "אחר":
        send_pic(file['כתובת'][rows[id]], message.chat.id)
        bot.set_state(id, MyStates.one_tagging, message.chat.id)
        bot.send_message(id, "do you see the feature in the pic?", reply_markup=markup_one_tagging)
        return

    # update the file
    update_addr_csv(parameters.tagging_option[inp], id)
    # go to the next untagged row
    rows[id] += pics_per_addr
    if check_rows(message):
        return
    send_pics(file['כתובת'][rows[id]], message.chat.id)
    if file[features[id]][rows[id]] != '-':
        bot.set_state(id, MyStates.check_tagging, message.chat.id)
        bot.send_message(id, "this image is tagged as " + see_tag(id) + "\nthe address is " + file['כתובת'][rows[id]],
                         reply_markup=check_markup)

    # make the next question
    else:
        bot.send_message(message.chat.id,
                         "do you see the feature in the pics? \nthe address is " + file['כתובת'][rows[id]])


# check - tagging part
check_markup = make_markup()
check_markup.add('נכון', 'אחר')


@bot.message_handler(state=MyStates.check_tagging)
def check_tag(message):
    print('checking state')
    inp = message.text
    id = message.from_user.id

    if inp == "אחר":
        send_pic(file['כתובת'][rows[id]], message.chat.id)
        bot.set_state(id, MyStates.one_tagging, message.chat.id)
        bot.send_message(id, "do you see the feature in the pic?", reply_markup=markup_one_tagging)
        return
    if inp != 'נכון':
        # update the file
        update_addr_csv(parameters.tagging_option[inp], id)

    # go to the next untagged row
    rows[id] += pics_per_addr
    if check_rows(message):
        return
    if file[features[id]][rows[id]] == '-':
        print(1)
        bot.set_state(id, MyStates.tagging, message.chat.id)
        bot.send_message(message.chat.id, "you checked all the tagged images. very nice!")
        send_pics(file['כתובת'][rows[id]], message.chat.id)
        bot.send_message(message.chat.id, "do you see the feature in the pics? \nthe address is " + file['כתובת'][
            rows[id]], reply_markup=markup_tagging)
    else:
        # make the next question
        send_pics(file['כתובת'][rows[id]], message.chat.id)
        bot.send_message(id, "this image is tagged as " + see_tag(id) + "\nthe address is " + file['כתובת'][rows[id]] +
                         ' and the image index is ' + str(int(((rows[id] / pics_per_addr) + 1))))


def see_tag(id):
    same = True
    for i in range(5):
        if file[features[id]][rows[id] + i] != file[features[id]][rows[id] + i + 1]:
            same = False
    if same:
        return file[features[id]][rows[id]]
    else:
        msg = '\n'
        for i in range(6):
            msg += file[features[id]][rows[id] + i] + ' '
        return msg + '\n'


# image - tagging part
def send_pic(addr, id):
    directory = parameters.untagged_photos_dir
    global one_tag_index
    f = os.path.join(directory, addr)
    for imagefile in os.listdir(f):
        path = os.path.join(f, imagefile)
        if 'gsv_' + str(one_tag_index) not in imagefile:
            continue
        photo = open(path, 'rb')
        bot.send_photo(id, photo)


markup_one_tagging = make_markup()
one_tag_index = 0


@bot.message_handler(state=MyStates.one_tagging)
def one_tagging(message):
    print('one pic tagging state')
    global one_tag_index
    inp = message.text
    id = message.from_user.id
    # update the file
    file[features[id]][rows[id]] = parameters.tagging_option[inp]
    # make the next question
    one_tag_index += 1
    rows[id] += 1
    if one_tag_index == 6:
        one_tag_index = 0
        send_pics(file["כתובת"][rows[id]], message.chat.id)
        if file[features[id]][rows[id]] == '-':
            bot.set_state(id, MyStates.tagging, message.chat.id)
            bot.send_message(message.chat.id, "do you see the feature in the pics? \nthe address is " + file['כתובת'][
                rows[id]], reply_markup=markup_tagging)
        else:
            bot.set_state(id, MyStates.check_tagging, message.chat.id)
            bot.send_message(id,
                             "this image is tagged as " + see_tag(id) + "\nthe address is " + file['כתובת'][rows[id]],
                             reply_markup=check_markup)

        return

    send_pic(file['כתובת'][rows[id]], message.chat.id)
    bot.send_message(id, "do you see the feature in the pic?")


# get predict data part
def make_nei_markup(nei_list):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = []
    for name in nei_list:
        buttons.append(types.KeyboardButton(name))
    mod = len(buttons) % 3
    for i in range(0, len(buttons) - mod, 3):
        markup.add(buttons[i], buttons[i + 1], buttons[i + 2])
    if mod == 1:
        markup.add(buttons[len(buttons) - 1])
    elif mod == 2:
        markup.add(buttons[len(buttons) - 2], buttons[len(buttons) - 1])
    return markup


nei_markup = make_nei_markup(database.get_neighborhoods_list())


@bot.message_handler(state=MyStates.choose_data_feature)
def choose_data_feature(message):
    print('choose data feature state')
    id = message.from_user.id
    features[id] = message.text
    bot.send_message(id, "choose which neighborhood you want to see", reply_markup=nei_markup)
    bot.set_state(id, MyStates.choose_data_nbrh, message.chat.id)


@bot.message_handler(state=MyStates.choose_data_nbrh)
def choose_data_nei(message):
    print('choose neighborhood state')
    id = message.from_user.id
    neighborhood = message.text
    if features[id] == 'all':
        df = database.get_neighborhood_rows(neighborhood)
    else:
        df = database.get_nf_rows(neighborhood, features[id])
    print(df['model id'])
    print(type(df['model id'][1]))
    df.to_excel(parameters.result_csv)
    file = open(parameters.result_csv, 'rb')
    bot.send_document(id, file)


    # max_length = 4096
    #
    # substrings = [ans[i:i + max_length] for i in range(0, len(ans), max_length)]
    # for string in substrings:
    #     bot.send_message(id, '```'+string+'```')
    bot.send_message(id, "choose which neighborhood you want to see now?")


# bot part
bot.add_custom_filter(custom_filters.StateFilter(bot))
bot.infinity_polling(skip_pending=True)

