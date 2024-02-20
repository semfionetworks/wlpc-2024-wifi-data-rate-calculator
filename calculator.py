import streamlit as st
from streamlit_extras.stylable_container import stylable_container
import pandas as pd
import yaml

def get_client_device_details(client_name: str, client_devices: list) -> dict:
    for client in client_devices:
        if client_name == f'{client["manufacturer"]} {client["name"]}':
            return client
    return {}

configs = yaml.safe_load(open('config.yml', 'r'))

st.set_page_config(layout="wide")
st.image("logo-semfio.png", width=200)
st.title("Wi-Fi Data Rates Calculator")

col1, col2 = st.columns(2)

with col1:
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

with col2:
    # Channel Width Selection
    channel_width_selection = st.selectbox(
        'Channel Width',
        ['20 MHz', '40 MHz', '80 MHz', '160 MHz', '320 MHz'],
        key='channel_width_selection'
    )

def get_mcs_indexes(
    client_device_details: dict,
    wifi_phys: list
) -> list:
    mcs_indexes = []
    if client_device_details['phy'] == 'HT':
        for phy in wifi_phys:
            if phy['name'] == 'HT':
                if client_device_details['nss'] == 1:
                    mcs_indexes = phy['mcs_index'][0:8]
                elif client_device_details['nss'] == 2:
                    mcs_indexes = phy['mcs_index'][0:16]
                elif client_device_details['nss'] == 3:
                    mcs_indexes = phy['mcs_index'][0:24]
                elif client_device_details['nss'] == 4:
                    mcs_indexes = phy['mcs_index'][0:32]
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

def get_nss_list(client_device_details: dict) -> list:
    nss_list = []
    if client_device_details['phy'] == "HT":
        for i in range(1,client_device_details['nss'] + 1):
            for j in range(0,8):
                nss_list.append(i)
    elif client_device_details['phy'] == "VHT":
        for i in range(1,client_device_details['nss'] + 1):
            for j in range(0,10):
                nss_list.append(i)
    elif client_device_details['phy'] == "HE":
        for i in range(1,client_device_details['nss'] + 1):
            for j in range(0,12):
                nss_list.append(i)
    elif client_device_details['phy'] == "EHT":
        for i in range(1,client_device_details['nss'] + 1):
            for j in range(0,14):
                nss_list.append(i)
    return nss_list

# Display the MCS Table
mcs_indexes = get_mcs_indexes(client_device_details, configs['wifi_phys'])
phy_list = get_phy_list(client_device_details,  mcs_indexes)
modulations = get_modulations(client_device_details, mcs_indexes, configs)
coding_rates = get_coding_rates(client_device_details, mcs_indexes, configs)
nss_list = get_nss_list(client_device_details)
df = pd.DataFrame(
    {
        'PHY': phy_list,
        'MCS Index': mcs_indexes,
        'Modulation': modulations,
        'Coding': coding_rates,
        'Spatial Streams': nss_list
    }
)

# df_styled = df.style.applymap(lambda x: 'background-color: red' if x == 'HE' else '', subset=['PHY'])
# df_styled = df.style.set_properties(**{'text-align': 'center'})


st.toast(f'New data rates calculated for {client_device_option} for a {channel_width_selection} wide channel.')

with stylable_container(
    key='mcs_table',
    css_styles=''''
        table {
            border-collapse: collapse;
        }

        th, td {
          text-align: center;
        }
    '''
):
    st.write(df.to_html(index=False), unsafe_allow_html=True)
