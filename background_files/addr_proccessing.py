# requests and json are the dependencies

import re


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


def add_city_suffix(address):
    if "תל אביב יפו" not in address:
        if "תל אביב" not in address:
            return address + " תל אביב יפו"
        else:
            return address + " יפו"
    return address


def process_addresses(addresses):
    def expand_address(full_address):
        match = re.search(r'(\d+)-(\d+)', full_address[1])
        if match:
            start_num, end_num = match.groups()
            expanded_addresses = [re.sub(r'(\d+)-(\d+)', str(num), full_address[1]) for num in
                                  range(int(start_num), int(end_num) + 1)]
            expanded_full_addresses = [[full_address[0], addr] for addr in expanded_addresses]
            return expanded_full_addresses
        else:
            return [full_address] if any(char.isdigit() for char in full_address[1]) else []

    processed_addresses = [addr for address in addresses for addr in expand_address(address) if addr]
    # processed_addresses = [address + " תל אביב יפו" if "תל אביב" not in address else address for address in
    #                       expanded_addresses]

    return processed_addresses


def clear_special_chars(input_string):
    forbidden_chars = {'<', '>', ':', '"', '/', '\\', '|', '?', '*', ','}
    cleaned_string = ''.join(char for char in input_string if char not in forbidden_chars)
    return cleaned_string
