import streamlit as st
import utils as utils
import pandas as pd
import polars as pl
from io import BytesIO
import xlsxwriter
import openpyxl
import ThaiTextPrepKit

__version__ = '1.0a'

def on_file_uploader_change():
    print('Change!')
    st.session_state.performed_dataframe = None
    st.session_state.perform = False

st.header(f"Text Preprocessing {__version__} 🥳")
st.write("Thai language preprocessing for any downstream tasks")
st.write(f'Text Preprocessing Version: {ThaiTextPrepKit.__version__}')

# Insert containers separated into tabs:
tab1, tab2 = st.tabs(["Text Preprocessing", "Data View"])

with tab1:
    uploaded_file = st.file_uploader('Upload file here', type=['csv', 'xlsx'],
                    accept_multiple_files=False,
                    on_change=on_file_uploader_change)

    COLUMNS = []
    dataframe = None

    # Initialize session state for the variable
    if 'performed_dataframe' not in st.session_state:
        st.session_state.performed_dataframe = None
        #performed_dataframe = None

    if 'perform' not in st.session_state:
        st.session_state.perform = False

    # Function to set the variable
    def set_performed_dataframe(value):
        st.session_state.performed_dataframe = value

    if uploaded_file is not None:
        try:
            file_type = uploaded_file.type
            if file_type == 'text/csv':
                dataframe = pl.read_csv(uploaded_file)

            elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                workbook = openpyxl.load_workbook(uploaded_file)
                
                selected_sheet = st.selectbox(
                    "Select sheet",
                    workbook.sheetnames,
                    index=0,
                    #placeholder="Select sheet...",
                )

                if selected_sheet:
                    dataframe = pl.read_excel(uploaded_file,
                                            sheet_name=selected_sheet,
                                            engine='calamine')

            st.write('Sample data')
            st.dataframe(dataframe.head(5))
            #st.data_editor(dataframe.head(5),
            #               disabled=True)
            
            COLUMNS = dataframe.columns

            st.session_state.perform = True

        except Exception as error:
            st.write(error)
            st.session_state.perform = False

    else:
        st.session_state.perform = False
        st.session_state.performed_dataframe = None

    text_column = st.selectbox(
    "Select text column",
    COLUMNS,
    index=0,
    placeholder="Select text column...",
    )

    st.write("You selected:", text_column)

    output_column = st.text_input("Output column title", "pre_text")

    remain_stopwords = st.checkbox('Remain Stopwords',
                                value=True)

    lowercase = st.checkbox('Lowercase Text',
                                value=False)

    remain_format = st.checkbox('Remain Text Format',
                                value=True)

    return_token_list = st.checkbox('Return Token List',
                                value=False)

    include_pattern = st.text_input('Include Pattern',
                                    placeholder='Input pattern to remain here... e.g. /()')

    spec_patterns = st.selectbox(
    "Select Specific Pattern",
    ('default', 'natural', 'corporate'),
    index=0,
    placeholder="Select specific patterns...",
    )

    perform_ready = not st.session_state.perform

    perform_button = st.button("Perform Preprossing", 
                            type="primary",
                            key='perform_button',
                            disabled=perform_ready)

    if perform_button:
        if dataframe is not None:
            #try:
                performed_dataframe = utils.preprocess(df=dataframe,
                                input_col=text_column,
                                output_col=output_column,
                                custom_dict=None,
                                keep_stopwords=remain_stopwords,
                                keep_format=remain_format,
                                return_token_list=return_token_list,
                                include_pattern=include_pattern,
                                lower_case=lowercase,
                                patterns=spec_patterns)
                
                set_performed_dataframe(performed_dataframe)

                #st.data_editor(dataframe[output_column].head(5),
                #               disabled=True)

            #except Exception as error:
            #    st.write(f'⚠️ Exception Occur: {error}')

        else:
            st.write('⚠️ Upload file first!')

    #st.write(st.session_state.performed_dataframe)
    performed_dataframe = st.session_state.performed_dataframe

    if performed_dataframe is not None:
        if output_column in performed_dataframe.columns:
            st.dataframe(performed_dataframe.select([text_column, output_column]).head(5))

            download_csv = st.download_button('Donwload .CSV',
                                                data=utils.convert_to_csv(performed_dataframe),
                                                file_name="preprocess_text.csv",
                                                mime="text/csv",
                                                type='secondary')

            download_xlsx = st.download_button('Donwload .XLSX',
                                                data=utils.convert_to_xlsx(performed_dataframe),
                                                file_name="preprocess_text.xlsx",
                                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                                type='secondary')
            
            download_html_table = st.download_button('Get HTML Table',
                                                    data=utils.to_html_highlight_table(performed_dataframe,
                                                                                        patterns=spec_patterns,
                                                                                        raw_column=text_column,
                                                                                        preprocess_column=output_column),
                                                    file_name='HTML_compare_table.html')
            
with tab2:
    df = st.session_state.get('performed_dataframe')
    if df is not None:
        st.dataframe(df)