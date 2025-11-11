import streamlit as st
import pandas as pd
import numpy as np
from streamlit_extras.stylable_container import stylable_container
import gspread
from google.oauth2.service_account import Credentials
import datetime as dt
import utils

p1_id = 38
p2_id = 42

p1_name = (
    utils.read_sheet("TABLE_PLAYERS")[
        utils.read_sheet("TABLE_PLAYERS")["id_player"] == p1_id
    ]
    .reset_index(drop=True)["name"]
    .loc[0]
)
p2_name = (
    utils.read_sheet("TABLE_PLAYERS")[
        utils.read_sheet("TABLE_PLAYERS")["id_player"] == p2_id
    ]
    .reset_index(drop=True)["name"]
    .loc[0]
)
print(p1_name, p2_name)
