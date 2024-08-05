from ThaiTextPrepKit import typo_patterns as TYPO
from ThaiTextPrepKit.polars_pretextkit import thai_text_preprocessing, preprocess_text_batches
import polars as pl
import streamlit as st
import pandas as pd
from io import BytesIO
import re
import mmh3
import openpyxl

available_patterns = {
    'default': TYPO.patterns,
    'natural': TYPO.natural_patterns,
    'corporate': TYPO.corp_patterns,
}

def hash_dataframe(df: pl.DataFrame, seed=42) -> str:
    """Hash a polars DataFrame. Due to the behaviour of pl.DataFrame.hash_rows 
    this will only be consistent given a polars version.
    Args:
        df (pl.DataFrame): polars DataFrame to be hashed.
        seed (int, optional): Seed for the hash function.
    Returns:
        str: Hash of the polars DataFrame.
    """
    row_hashes = df.hash_rows(seed=seed)
    hasher = mmh3.mmh3_x64_128(seed=seed)
    for row_hash in row_hashes:
        hasher.update(row_hash.to_bytes(64, "little"))
    return hasher.digest().hex()

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def load_uploaded_file(uploaded_file, file_type, selected_sheet=None):
    if file_type == 'text/csv':
        dataframe = pl.read_csv(uploaded_file)
        return dataframe

    elif file_type == 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet':
        workbook = openpyxl.load_workbook(uploaded_file)
        return workbook
    
    elif file_type == 'excel':
        dataframe = pl.read_excel(uploaded_file,
                        sheet_name=selected_sheet,
                        engine='calamine')
        return dataframe

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def preprocess(df, 
               input_col,
               output_col,
               custom_dict=None,
               keep_stopwords: bool=True,
               keep_format: bool=True,
               return_token_list: bool=False,
               patterns=None,
               **kwargs):
    patterns = available_patterns.get(patterns)
    df = df.pipe(thai_text_preprocessing,
                                 input_col,
                                 output_col,
                                 custom_dict=custom_dict,
                                 keep_stopwords=keep_stopwords,
                                 keep_format=keep_format,
                                 return_token_list=return_token_list,
                                 patterns=patterns,
                                 **kwargs)
    
    return df #df.to_pandas()

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def sigle_text_preprocessing(text,
                            keep_stopwords: bool=True,
                            keep_format: bool=True,
                            return_token_list: bool=False,
                            lower_case: bool=False,
                            include_pattern: str=None,
                            patterns=None,):
    
    patterns = available_patterns.get(patterns)
 
    pre_series = preprocess_text_batches(series=pl.Series([text]),
                                   #custom_dict=None,
                                   keep_stopwords=keep_stopwords,
                                   keep_format=keep_format,
                                   return_token_list=return_token_list,
                                   lower_case=lower_case,
                                   include_pattern=include_pattern,
                                   patterns=patterns)
    return pre_series

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def convert_to_csv(df: pl.DataFrame):
    # IMPORTANT: Cache the conversion to prevent computation on every rerun
    return df.write_csv() #df.to_csv().encode("utf-8")

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def convert_to_xlsx(df: pl.DataFrame):
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        # Write each dataframe to a different worksheet.
        df.to_pandas().to_excel(writer, sheet_name='Sheet1', index=False)
    return buffer

##################################
##### FOR HTML COMPARE TABLE #####
##################################
def highlight_patterns(patterns, text, html=True, highlight_color_replace="#FFFF00", highlight_color_match="#00FFFF"):
    """
    Highlights all occurrences of the given regex patterns in the text using HTML <span> tags with background color.

    :param patterns: A list of tuples containing regex patterns and their replacements.
    :param text: The text to search within.
    :param highlight_color_replace: The background color to use for replacements (default is yellow).
    :param highlight_color_match: The background color to use for matches without replacement (default is blue).
    :return: The text with highlighted matches.
    """
    def add_highlight(match, color):
        return f'<span style="background-color: {color};">{match.group(0)}</span>' if html else f'<typo>{match.group(0)}</typo>'
    
    highlighted_text = text
    for pattern, replacement in patterns:
        matches = list(re.finditer(pattern, text))
        replacement = replacement.lstrip('<IGNORE>').rstrip('</IGNORE>')
        #print(replacement)
        if matches:
            for match in matches:
                if replacement in match.group(0):
                    highlighted_text = highlighted_text.replace(match.group(0), add_highlight(match, highlight_color_match))
                else:
                    highlighted_text = highlighted_text.replace(match.group(0), add_highlight(match, highlight_color_replace))
    
    return highlighted_text

def generate_html_table(*args):
    """
    Generate an HTML table with columns for each text list provided, using the given names as headers.

    Args:
    - *args (tuple): Variable number of tuples, each containing a list of texts and a corresponding name.

    Returns:
    - html_content (str): String containing the HTML table.
    """
    headers = [name for _, name in args]
    
    html_content = "<table border='1'>\n"
    html_content += "<tr>" + "".join(f"<th>{header}</th>" for header in headers) + "</tr>\n"
    
    # Find the maximum length among the provided lists to handle uneven lengths
    max_length = max(len(text_list) for text_list, _ in args)
    
    for i in range(max_length):
        html_content += "<tr>"
        for text_list, _ in args:
            cell_content = text_list[i] if i < len(text_list) else ""
            html_content += f"<td>{cell_content}</td>"
        html_content += "</tr>\n"

    html_content += "</table>"
    
    return html_content

def get_highlight_texts(patterns, texts: list) -> None:
    html_text = []
    for text in texts:
        html_text.append(highlight_patterns(patterns, text))
    return html_text

@st.cache_data(hash_funcs={pl.DataFrame: hash_dataframe})
def to_html_highlight_table(df, patterns, raw_column, preprocess_column):
    patterns = available_patterns.get(patterns)

    df = df.drop_nulls([raw_column, preprocess_column])

    # Generate HTML table
    html_table = generate_html_table(
        (get_highlight_texts(patterns, df.get_column(raw_column).to_list()), 'Raw Text'),
        (get_highlight_texts(patterns, df.get_column(preprocess_column).to_list()), "PAREPA"),
        )
    
    return html_table