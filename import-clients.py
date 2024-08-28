import csv
import yaml


def get_device_nss(nss_input: str) -> int:
    if not nss_input.isdigit():
        return -1
    else:
        return int(nss_input)


def get_device_phy(phy_input: str) -> str:
    if phy_input == "n":
        return "HT"
    elif phy_input == "ac":
        return "VHT"
    elif phy_input == "ax":
        return "HE"
    elif phy_input == "be":
        return "EHT"
    else:
        return ""


def get_device_max_tx(max_tx_input: str) -> int:
    if not max_tx_input.isdigit():
        return -1
    else:
        return int(max_tx_input)


def get_device_name(name_input: str) -> tuple:
    print(name_input.split())
    name_split = name_input.split()
    output = ("", "")
    if len(name_split) == 1:
        if "roku" in name_split[0]:
            output = ("Roku", name_split[0])
        else:
            output = ("", name_split[0])
    elif len(name_split) == 2:
        if name_split[0] == "iPhone":
            output = ("Apple", f"{name_split[0]} {name_split[1]}")
        else:
            output = (name_split[0], name_split[1])
    elif len(name_split) == 3:
        if name_split[0] == "iPhone":
            output = (
                "Apple", f"{name_split[0]} {name_split[1]}{name_split[2]}")
        else:
            output = (name_split[0], f"{name_split[1]} {name_split[2]}")
    else:
        output = ("", "")
    print(output)
    return output


devices = []

with open('ClientsList - Clients.csv', 'r') as csvfile:
    reader = csv.reader(csvfile)
    # Loop through each row in the CSV file
    for row in reader:
        device_info = {}

        # Check if this is not the first line (header) in the CSV file
        if row[0] != "Device":
            # Extract information from the row
            device_info['manufacturer'], device_info['name'] = get_device_name(
                row[0])
            device_info['phy'] = get_device_phy(row[27])
            device_info['nss'] = get_device_nss(row[26])
            device_info['max_tx'] = get_device_max_tx(row[33])
            # Add the extracted information to the devices list
            if device_info['manufacturer'] != "":
                devices.append(device_info)

client_devices_yaml = yaml.dump(
    {"client_devices": devices}
)

with open('output.yaml', 'w') as yamlfile:
    yamlfile.write(client_devices_yaml)
