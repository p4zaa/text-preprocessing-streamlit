import streamlit as st
import utils as utils
import pandas as pd
from io import BytesIO
import xlsxwriter
import openpyxl

st.header("Text Preprocessing 👏")
st.write("Thai language preprocessing for any downstream tasks")

uploaded_file = st.file_uploader('Upload file here', type=['csv', 'xlsx'],
                 accept_multiple_files=False)

COLUMNS = []
dataframe = None

if uploaded_file is not None:
    file_type = uploaded_file.type
    if file_type == 'text/csv':
        dataframe = pd.read_csv(uploaded_file)

    elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        workbook = openpyxl.load_workbook(uploaded_file)
        
        selected_sheet = st.selectbox(
            "Select sheet",
            workbook.sheetnames,
            index=0,
            #placeholder="Select sheet...",
        )

        if selected_sheet:
            dataframe = pd.read_excel(uploaded_file)

    st.write('Sample data')
    st.data_editor(dataframe.head(5),
                   disabled=True)
    
    COLUMNS = dataframe.columns

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
                               value=True)

remain_format = st.checkbox('Remiain Text Format',
                               value=True)

return_token_list = st.checkbox('Return Token List',
                               value=False)

include_pattern = st.text_area('Include Pattern')

spec_patterns = st.selectbox(
   "Select Specific Pattern",
   ('default', 'corporation'),
   index=0,
   placeholder="Select specific patterns...",
)

perform_button = st.button("Perform Preprossing", 
                           type="primary",
                           key='perform_button')

if perform_button:
    if dataframe is not None:
        #try:
            dataframe = utils.preprocess(df=dataframe,
                            input_col=text_column,
                            output_col=output_column,
                            custom_dict=None,
                            keep_stopwords=remain_stopwords,
                            keep_format=remain_format,
                            return_token_list=return_token_list,
                            include_pattern=include_pattern,
                            pattern=spec_patterns)
            
            st.data_editor(dataframe[output_column].head(5),
                           disabled=True)

        #except Exception as error:
        #    st.write(f'⚠️ Exception Occur: {error}')

    else:
        st.write('⚠️ Upload file first!')

if dataframe is not None:
    if output_column in dataframe.columns:
        st.dataframe(dataframe[[text_column, output_column]].head(5))
    download_csv = st.download_button('Donwload .CSV',
                                        data=utils.convert_to_csv(dataframe),
                                        file_name="preprocess_text.csv",
                                        mime="text/csv",
                                        type='secondary')

    download_xlsx = st.download_button('Donwload .XLSX',
                                        data=utils.convert_to_xlsx(dataframe),
                                        file_name="preprocess_text.xlsx",
                                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                        type='secondary')