import streamlit as st
from page.PreProccessing import Preprocess
import torch
import os
import wfdb
import pandas as pd
from electroCardioGuard.PersonIdentification import PersonIdentification
from page.Descriptive_Analysis import DescriptiveAnalysis
from page.arrythmia_detection import ArrhythmiaAnalysis
from page.Predictive_Analysis import PredictiveAnalysis
from page.Myocardial_Infarction import CNN_LSTM, load_model, predict, encoder, MyocardialInfarction
from streamlit_extras.metric_cards import style_metric_cards

DATASET_PATH = r"C:\Users\User\PycharmProjects\ECGProject\mit-bih-arrhythmia-database-1.0.0"

# Streamlit config
st.set_page_config(layout="wide")
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Preprocessing", "🗃 Descriptive Analysis",
    "📊 Arrhythmia Detection", "📊 Myocardial Infarction Detection",
    "📊 Person Identification"
])

# Initialize saved_signals in session state if not already present
if 'saved_signals' not in st.session_state:
    st.session_state.saved_signals = []

# Function to load ECG signals from directory and save them in session state
def preload_ecg_signals(dataset_path):
    signals = []
    for filename in os.listdir(dataset_path):
        if filename.endswith(".dat"):
            patient_id = filename.split(".")[0]
            record = wfdb.rdrecord(os.path.join(dataset_path, patient_id))
            signal_data = {
                "patient_id": patient_id,
                "signal": record.p_signal,
                "fs": record.fs
            }
            signals.append(signal_data)
    st.session_state.saved_signals = signals
    DATA = {"record": record, "channel": 0, "saved_signals": st.session_state.saved_signals}

    return DATA

# Preload ECG signals if not already loaded
if not st.session_state.saved_signals:
    data=preload_ecg_signals(DATASET_PATH)
    page = Preprocess(data)
    signal = page.content()

# Helper function to save signals dynamically
def save_signal(option, signal):
    update = False
    for s in st.session_state.saved_signals:
        if s["patient_id"] == option:
            update = True
            s["signal"] = signal
            break
    if not update:
        st.session_state.saved_signals.append({"patient_id": option, "signal": signal})
    return st.session_state.saved_signals

with tab1:
    st.write("Upload your ECG data files (WFDB format) for analysis.")

    uploaded_files = st.file_uploader(
        "Choose ECG data files", type=["dat", "hea", "xyz"], accept_multiple_files=True
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.type == "application/octet-stream":
                dat_file = uploaded_file
                hea_file = next(
                    (f for f in uploaded_files if f.name == uploaded_file.name.replace('.dat', '.hea')), None
                )
                if hea_file:
                    st.write(f"Uploaded files: {hea_file.name}, {dat_file.name}")

                    with open(dat_file.name, 'wb') as f:
                        f.write(dat_file.read())
                    with open(hea_file.name, 'wb') as f:
                        f.write(hea_file.read())

                    record = wfdb.rdrecord(dat_file.name.replace('.dat', ''))
                    DATA = {"record": record, "channel": 0, "saved_signals": st.session_state.saved_signals}

                    page = Preprocess(DATA)
                    signal = page.content()

                    if st.button('Save'):
                        st.session_state.saved_signals = save_signal(dat_file.name.split('.')[0], signal)

                    os.remove(dat_file.name)
                    os.remove(hea_file.name)

    rows = [[s["patient_id"]] for s in st.session_state.saved_signals]
    df1 = pd.DataFrame(rows, columns=["patient_id"])
    st.table(df1)

with tab2:
    if not st.session_state.saved_signals:
        st.error("Please upload or load a record first.")
    else:
        DATA = {"record": record, "signal": signal, 'saved_signals': st.session_state.saved_signals}
        st.title("ECG Signal Analysis")
        page = DescriptiveAnalysis(DATA)
        page.content()

with tab3:
    if not st.session_state.saved_signals:
        st.error("Please upload or load a record first.")
    else:
        DATA = {"record": record, "signal": signal, 'saved_signals': st.session_state.saved_signals}
        page = ArrhythmiaAnalysis(DATA)
        page.content()

with tab4:
    if not st.session_state.saved_signals:
        st.error("Please upload or load a record first.")
    else:
        DATA = {"record": record, "signal": signal, 'saved_signals': st.session_state.saved_signals}
        page = MyocardialInfarction(DATA)
        page.content()

with tab5:
    if not st.session_state.saved_signals:
        st.error("Please upload or load a record first.")
    else:
        DATA = {"record": record, "signal": signal, 'saved_signals': st.session_state.saved_signals}
        page = PersonIdentification(DATA)
        page.content()
