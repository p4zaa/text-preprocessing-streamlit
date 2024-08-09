import streamlit as st
import utils as utils
import pandas as pd
import polars as pl
from io import BytesIO
import xlsxwriter
#import openpyxl
import ThaiTextPrepKit

__version__ = '1.0H'

def on_file_uploader_change():
    print('Change!')
    st.session_state.performed_dataframe = None
    st.session_state.perform = False

st.header(f"Text Preprocessing {__version__} 🥳")
st.write("Thai language preprocessing for any downstream tasks")
st.write(f'Text Preprocessing Version: {ThaiTextPrepKit.__version__}')

# Insert containers separated into tabs:
tab1, tab2, tab3, tab4 = st.tabs(["Text Preprocessing", "Data View", "Test Here", "Pattern Replacements"])

with tab1:
    uploaded_file = st.file_uploader('Upload file here', type=['csv', 'xlsx'],
                    accept_multiple_files=False,
                    on_change=on_file_uploader_change,
                    help='อัปโหลดไฟล์ในรูปแบบ .csv หรือ .xlsx (ได้ครั้งละ 1 ไฟล์)')

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
                dataframe = utils.load_uploaded_file(uploaded_file=uploaded_file,
                                                     file_type=file_type) #pl.read_csv(uploaded_file)

            elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
                workbook = utils.load_uploaded_file(uploaded_file=uploaded_file,
                                                    file_type=file_type) #openpyxl.load_workbook(uploaded_file)
                
                selected_sheet = st.selectbox(
                    "Select sheet",
                    workbook.sheetnames,
                    index=0,
                    help='เลือกชีทที่ต้องการ',
                    #placeholder="Select sheet...",
                )

                if selected_sheet:
                    dataframe = utils.load_uploaded_file(uploaded_file=uploaded_file,
                                                        file_type='excel',
                                                        selected_sheet=selected_sheet) 
                                #pl.read_excel(uploaded_file,
                                #            sheet_name=selected_sheet,
                                #            engine='calamine')

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

    text_columns = st.multiselect(
        "Select text columns",
        COLUMNS,
        help='เลือกคอลัมน์ข้อความที่ต้องการปรับปรุง',
    )

    st.write("You selected:", text_columns)

    #st.selectbox(
    #    "Select text column",
    #    COLUMNS,
    #    index=0,
    #    placeholder="Select text column...",
    #    help='เลือกคอลัมน์ข้อความที่ต้องการปรับปรุง'
    #)

    output_suffix = st.text_input("Output column suffix", "_pre_text",
                                  help='กำหนดข้อความต่อท้ายชื่อคอลัมน์สำหรับคอลัมน์ใหม่ เช่น คอลัมน์ text ชื่อคอลัมน์ที่ปรับปรุงข้อความแล้วชื่อ text_pre_text')

    remain_stopwords = st.checkbox('Remain Stopwords',
                                value=True,
                                help='เก็บคำเชื่อมไว้ เช่น และ, หรือ, ใช่, ไม่')

    lowercase = st.checkbox('Lowercase Text',
                                value=False,
                                help='แปลงตัวอักษรเป็นตัวพิมพ์เล็กทั้งหมด')

    remain_format = st.checkbox('Remain Text Format',
                                value=True,
                                help='คงรูปแบบการเว้นวรรคเดิมของประโยคต้นฉบับไว้ หากไม่เลือกประโยคจะเว้นวรรคแยกเป็นคำๆ เช่น "สบายดีไหม" -> "สบาย ดี ไหม"')

    return_token_list = st.checkbox('Return Token List',
                                value=False,
                                help='คือค่าประโยคในรูปแบบลิสต์ของคำ (สำหรับการนำไปใช้ต่อในการ visualization เท่านั้น) เช่น "สบายดีไหม" -> ["สบาย","ดี","ไหม"]')

    include_pattern = st.text_input('Include Pattern',
                                    placeholder='Input pattern to remain here... e.g. /()',
                                    value='/()',
                                    help='เพิ่มอักขระพิเศษที่ไม่ต้องการให้ตัดทิ้ง')

    spec_patterns = st.selectbox(
        "Select Specific Pattern",
        ('default', 'natural', 'corporate'),
        index=0,
        placeholder="Select specific patterns...",
    )

    st.info('default: The default pattern transforms the text for optimal data analysis and visualization.', icon="✨")
    st.info('natural: The natural pattern modifies and corrects the text while maintaining its original, smooth feel, making it ideal for real-world presentations.', icon="🍃")

    perform_ready = not st.session_state.perform

    perform_button = st.button("Perform Preprossing", 
                            type="primary",
                            key='perform_button',
                            disabled=perform_ready)

    output_columns = [col + output_suffix for col in text_columns]

    if perform_button:
        if dataframe is not None:
            #try:
            progress_text = "Operation in progress. Please wait."
            progress_bar = st.progress(0, text=progress_text)
            for i, text_column in enumerate(text_columns):
                progress_bar.progress(i + 1, text=progress_text)
                performed_dataframe = utils.preprocess(df=st.session_state.performed_dataframe if st.session_state.performed_dataframe is not None else dataframe,
                                input_col=text_column,
                                output_col=output_columns[i],
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
            progress_bar.empty()

        else:
            st.write('⚠️ Upload file first!')

    #st.write(st.session_state.performed_dataframe)
    performed_dataframe = st.session_state.performed_dataframe

    if performed_dataframe is not None:
        if st.session_state.performed_dataframe is not None:# and output_columns in performed_dataframe.columns:
            st.dataframe(performed_dataframe.select(output_columns).head(5))

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
            
            get_html_table = st.checkbox('Get HTML compare table',
                                        value=False)

            if get_html_table:
                if len(text_columns) == 1:
                    download_html_table = st.download_button('Get HTML Table',
                                                            data=utils.to_html_highlight_table(performed_dataframe,
                                                                                                patterns=spec_patterns,
                                                                                                raw_column=text_columns[0],
                                                                                                preprocess_column=output_columns[0]),
                                                            file_name='HTML_compare_table.html')
                    
                else:
                    st.warning('HTML table currently not support text column more than 1', icon="⚠️")
                
            #st.balloons()
            #dataframe = performed_dataframe
            
with tab2:
    df = st.session_state.get('performed_dataframe')
    if df is not None:
        st.dataframe(df.head(1000))

with tab3:
    input_text = st.text_area('Text',
                               placeholder='สวัสดีวันศุกร์',
                               value='เบอโทในแอพ',
                               help='พิมพ์ข้อความที่ต้องการทดสอบ',
                               height=10)
    
    test_remain_stopwords = st.checkbox('Remain Stopwords',
                                value=True,
                                help='เก็บคำเชื่อมไว้ เช่น และ, หรือ, ใช่, ไม่',
                                key='test_remain_stopwords')

    test_lowercase = st.checkbox('Lowercase Text',
                                value=False,
                                help='แปลงตัวอักษรเป็นตัวพิมพ์เล็กทั้งหมด',
                                key='test_lowercase')

    test_remain_format = st.checkbox('Remain Text Format',
                                value=True,
                                help='คงรูปแบบการเว้นวรรคเดิมของประโยคต้นฉบับไว้ หากไม่เลือกประโยคจะเว้นวรรคแยกเป็นคำๆ เช่น "สบายดีไหม" -> "สบาย ดี ไหม"',
                                key='test_remain_format')

    test_return_token_list = st.checkbox('Return Token List',
                                value=False,
                                help='คือค่าประโยคในรูปแบบลิสต์ของคำ (สำหรับการนำไปใช้ต่อในการ visualization เท่านั้น) เช่น "สบายดีไหม" -> ["สบาย","ดี","ไหม"]',
                                key='test_return_token_list')

    test_include_pattern = st.text_input('Include Pattern',
                                    placeholder='Input pattern to remain here... e.g. /()',
                                    value='/()',
                                    help='เพิ่มอักขระพิเศษที่ไม่ต้องการให้ตัดทิ้ง',
                                    key='test_include_pattern')

    test_spec_patterns = st.selectbox(
        "Select Specific Pattern",
        ('default', 'natural', 'corporate',),
        index=0,
        placeholder="Select specific patterns...",
        key='test_patterns'
    )

    st.info('default: The default pattern transforms the text for optimal data analysis and visualization.', icon="✨")
    st.info('natural: The natural pattern modifies and corrects the text while maintaining its original, smooth feel, making it ideal for real-world presentations.', icon="🍃")


    if input_text:
        series = utils.sigle_text_preprocessing(
            text=input_text,
            keep_stopwords=test_remain_stopwords,
            keep_format=test_remain_format,
            return_token_list=test_return_token_list,
            lower_case=test_lowercase,
            include_pattern=test_include_pattern,
            patterns=test_spec_patterns,
        )

        st.write()
        st.write(f'Output: {series[0]}')

with tab4:
    st.subheader(f'You are currently using text preprocessing version: {ThaiTextPrepKit.__version__}')
    st.link_button("Typo report/Request new pattern", 
                   "https://dustyblu3.notion.site/Word-Typo-Reports-8a61d91f7b4c4ae78da1d4ead5205966?pvs=4",
                   use_container_width=True,
                   type='primary',)

    default_tab, natural_tab, corporate_tab = st.tabs(["default", "natural", "corporate"])
    
    with default_tab:
        st.dataframe(utils.get_patterns_table('default'), 
                     use_container_width=True,
                     )

    with natural_tab:
        st.dataframe(utils.get_patterns_table('natural'),
                     use_container_width=True,)

    with corporate_tab:
        st.dataframe(utils.get_patterns_table('corporate'),
                     use_container_width=True,)