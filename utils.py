from ThaiTextPrepKit import polars_pretextkit as preprocess
from ThaiTextPrepKit.polars_pretextkit import thai_text_preprocessing
import polars as pl
import streamlit as st
import pandas as pd
from io import BytesIO

@st.cache_data
def preprocess(df, 
               input_col,
               output_col,
               custom_dict=None,
               keep_stopwords: bool=True,
               keep_format: bool=True,
               return_token_list: bool=False,
               **kwargs):
    df = pl.from_pandas(df).pipe(thai_text_preprocessing,
                                 input_col,
                                 output_col,
                                 custom_dict=custom_dict,
                                 keep_stopwords=keep_stopwords,
                                 keep_format=keep_format,
                                 return_token_list=return_token_list,
                                 **kwargs)
    
    return df.to_pandas()

@st.cache_data
def convert_to_csv(df: pd.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.to_csv().encode("utf-8")

@st.cache_data
def convert_to_xlsx(df: pd.DataFrame):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df.to_excel(writer, sheet_name='Sheet1', index=False)
    return buffer