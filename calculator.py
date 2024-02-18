import streamlit as st
import pandas as pd
import yaml

def get_ht_indexes(wifi_phys: list) -> list:
    ht_indexes = []
    for phy in wifi_phys:
        if phy['name'] == "HT":
            ht_indexes = phy['mcs_index']
    return ht_indexes

configs = yaml.safe_load(open('config.yml', 'r'))

st.title("Wi-Fi Data Rates Calculator")

client_device_option = st.selectbox('Which device do you want to calculate data rates for?',
    [f'{device["manufacturer"]} {device["name"]}' for device in configs['client_devices']]
)
