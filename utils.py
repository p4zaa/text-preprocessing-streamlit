from ThaiTextPrepKit import typo_patterns as TYPO
from ThaiTextPrepKit.polars_pretextkit import thai_text_preprocessing
import polars as pl
import streamlit as st
import pandas as pd
from io import BytesIO

available_patterns = {
    'default': TYPO.patterns,
    'corporate': TYPO.corp_patterns,
}

@st.cache_data
def preprocess(_df, 
               input_col,
               output_col,
               custom_dict=None,
               keep_stopwords: bool=True,
               keep_format: bool=True,
               return_token_list: bool=False,
               patterns=None,
               **kwargs):
    patterns = available_patterns.get(patterns)
    _df = _df.pipe(thai_text_preprocessing,
                                 input_col,
                                 output_col,
                                 custom_dict=custom_dict,
                                 keep_stopwords=keep_stopwords,
                                 keep_format=keep_format,
                                 return_token_list=return_token_list,
                                 patterns=patterns,
                                 **kwargs)
    
    return _df #df.to_pandas()

def convert_to_csv(_df: pl.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return _df.write_csv() #df.to_csv().encode("utf-8")

def convert_to_xlsx(_df: pl.DataFrame):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        _df.to_pandas().to_excel(writer, sheet_name='Sheet1', index=False)
    return buffer