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
        key='client_device_option',
        index = None
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
        key='channel_width_selection',
        index = None
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


def get_tdft_tgi_subcarrier_data_rate(
    client_device_details: dict,
    configs: dict,
    channel_width_selection : str
):
    type_calc = None
    for phy in configs["wifi_phys"]:
        if phy["name"] == client_device_details['phy']:
            if phy["ofdm"]:
                type_calc = "ofdm"
            if phy["ofdma"]:
                type_calc = "ofdma"
            break

    tdft = configs[f'{type_calc}_data']['tdft']
    tgi = configs[f'{type_calc}_data']['tgi']
    channel_width_number = int(channel_width_selection.replace("MHz", "").replace(" ", ""))
    number_data_subcarrier = 0
    if type_calc == "ofdm":
        for nsds_dict in configs[f'{type_calc}_data']["nsds"]:
            if nsds_dict["channel_width"] == channel_width_number:
                number_data_subcarrier = nsds_dict["nsd"]
                break

    if type_calc == "ofdma":
        for nsds_dict in configs[f'{type_calc}_data']["nsdus"]:
            if nsds_dict["channel_width"] == channel_width_number:
                number_data_subcarrier = nsds_dict["nsdu"]
                break

    return {'tdft' : tdft, 'tgi' : tgi, "number_data_subcarrier" : number_data_subcarrier}


def compute_data_rates(tdft_tgi_subcarrier_data_rate, df):
    for tgi_rate in tdft_tgi_subcarrier_data_rate["tgi"]:
        df[f'TGI {tgi_rate}'] = \
            round(tdft_tgi_subcarrier_data_rate["number_data_subcarrier"] * df['Spatial Streams'] * df['coding_numeric'] * df["nbpcs"]/\
            (tgi_rate + tdft_tgi_subcarrier_data_rate['tdft']), 1)
    return df


def get_nbpcs_for_modulations(modulations, configs):
    nbpcs_list = []
    for modulation in modulations:
        for config_modulation in configs["modulations"]:
            if modulation == config_modulation["name"]:
                nbpcs_list.append(config_modulation["nbpscs"])
    return nbpcs_list

def get_mcs_list(client_device_details, configs) -> list:
    mcs_list = []
    if client_device_details['phy'] == 'HT':
        mcs_list = get_mcs_indexes(client_device_details, configs['wifi_phys'])
    elif client_device_details['phy'] == 'VHT':
        mcs_list = [mcs for mcs in range(0,10)]
    elif client_device_details['phy'] == 'HE':
        mcs_list = [mcs for mcs in range(0,12)]
    elif client_device_details['phy'] == 'EHT':
        mcs_list = [mcs for mcs in range(0,14)]
    return mcs_list

# Display the MCS Table
if client_device_details != {} and channel_width_selection is not None:
    mcs_indexes = get_mcs_indexes(client_device_details, configs['wifi_phys'])
    phy_list = get_phy_list(client_device_details,  mcs_indexes)
    modulations = get_modulations(client_device_details, mcs_indexes, configs)
    coding_rates = get_coding_rates(client_device_details, mcs_indexes, configs)
    nss_list = get_nss_list(client_device_details)
    tdft_tgi_subcarrier_data_rate = get_tdft_tgi_subcarrier_data_rate(client_device_details, configs, channel_width_selection)
    nbpcs_list = get_nbpcs_for_modulations(modulations, configs)
    df = pd.DataFrame(
        {
            'PHY': phy_list,
            'MCS Index': mcs_indexes,
            'Nsd' : tdft_tgi_subcarrier_data_rate['number_data_subcarrier'],
            'Modulation': modulations,
            'Coding': coding_rates,
            'Spatial Streams': nss_list,
            'coding_numeric': [eval(x) for x in coding_rates],
            'nbpcs' : nbpcs_list
        }
    )
    df = compute_data_rates(tdft_tgi_subcarrier_data_rate, df)
    df.drop('coding_numeric', axis = 1, inplace = True)
    df.drop('Nsd', axis = 1, inplace = True)
    df.drop('nbpcs', axis = 1, inplace = True)

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
        with col2:
            list_nss = [nss for nss in range(1 ,client_device_details['nss'] + 1)]
            nss_filter = st.multiselect(
                'Number of Spatial Streams',
                list_nss,
                default=list_nss
            )
            gi_list = [0.8, 1.2, 3.2] if client_device_details['phy'] in ['HE', 'EHT'] else [0.4, 0.8]
            guard_interval_filter = st.multiselect(
                'Guard Interval',
                gi_list,
                default=gi_list
            )
            list_mcs = get_mcs_list(client_device_details, configs)
            mcs_index_filter = st.multiselect(
                'MCS Index',
                list_mcs,
                default=list_mcs
            )

        with col1:
            st.write(df.to_html(index=False), unsafe_allow_html=True)
