import streamlit as st
import pandas as pd
import yaml

def get_client_device_details(client_name: str, client_devices: list) -> dict:
    for client in client_devices:
        if client_name == f'{client["manufacturer"]} {client["name"]}':
            return client
    return {}

configs = yaml.safe_load(open('config.yml', 'r'))

st.title("Wi-Fi Data Rates Calculator")

# Client Device Selection
options = [f'{device["manufacturer"]} {device["name"]}' for device in configs['client_devices']]
client_device_option = st.selectbox(
    'Which device do you want to calculate data rates for?',
    options,
    key='client_device_option'
)

# Get client details
client_device_details = get_client_device_details(
    client_device_option,
    configs['client_devices']
)

# Channel Width Selection
channel_width_selection = st.selectbox(
    'Channel Width',
    ['20 MHz', '40 MHz', '80 MHz', '160 MHz', '320 MHz']
)

def get_mcs_indexes(
    client_device_details: dict,
    wifi_phys: list
) -> list:
    mcs_indexes = []
    if client_device_details['phy'] == 'HT':
        for phy in wifi_phys:
            if phy['name'] == 'HT':
                mcs_indexes = phy['mcs_index']
    else:
        for phy in wifi_phys:
            if phy['name'] == client_device_details['phy']:
                mcs_indexes = phy['mcs_index']*client_device_details['nss']
    return mcs_indexes

def get_modulations(client_device_details: dict, mcs_indexes:list, configs: dict) -> list:
    modulations = []
    for mcs_index in mcs_indexes:
        for index in configs['mcs_index']:
            if index['index'] == mcs_index:
                modulations.append(index['modulation'])
    return modulations

def get_coding_rates(client_device_details: dict, mcs_indexes:list, configs: dict) -> list:
    coding_rates = []
    for mcs_index in mcs_indexes:
        for index in configs['mcs_index']:
            if index['index'] == mcs_index:
                coding_rates.append(index['coding'])
    return coding_rates

def get_phy_list(client_device_details: dict,  mcs_indexes: list) -> list:
    phy_list = []
    for mcs_index in mcs_indexes:
        phy_list.append(client_device_details['phy'])
    return phy_list

def get_nss_list(client_device_details: dict,  mcs_indexes: list) -> list:
    nss_list = []

    return nss_list

# Display the MCS Table
mcs_indexes = get_mcs_indexes(client_device_details, configs['wifi_phys'])
phy_list = get_phy_list(client_device_details,  mcs_indexes)
modulations = get_modulations(client_device_details, mcs_indexes, configs)
coding_rates = get_coding_rates(client_device_details, mcs_indexes, configs)
nss_list = get_nss_list(client_device_details, mcs_indexes)
df = pd.DataFrame(
    {
        'PHY': phy_list,
        'MCS Index': mcs_indexes,
        'Modulation': modulations,
        'Coding': coding_rates,
        # 'Spatial Streams': nss_list
    }
)

with st.container():
    st.write(df.to_html(index=False), unsafe_allow_html=True)
