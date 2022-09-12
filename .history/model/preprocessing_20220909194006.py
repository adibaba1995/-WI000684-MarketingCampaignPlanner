# Dependencies
import streamlit as st
import pandas as pd
import plotly.express as px
import controller.preprocess as preProcess
from inform import Descriptions
import ast

def display_preprocessing():

    """
    display_preprocessing()  displays the preprocessing
    page and calls functions with actual functionality 
    which are defined after this function.
    """

    st.title('Preprocessing')
    st.markdown('---')

    data = select_user_journey()

    if (data is not None):
        display_data(data)
        run_diagnostics(data)
        cleaned = handle(data)

        if (cleaned is None):
            st.write('---')
            st.warning('Can not download the data, as it was not cleaned yet!')
        else:
            st.write(cleaned)
            csv = cleaned.to_csv().encode('utf-8')
            st.download_button(
                "Press to Download",
                csv,
                "cleaned_data.csv",
                "text/csv",
                key='clean-data'
            ) 

    else:
        st.markdown('---')
        st.warning('Before we start, you need to feed the processor some data!')

def select_user_journey():

    """
    select_user_journey() allows the user to drag-and-drop
    his data into the application.
    """

    c1, c2 = st.columns((2, 1))
    c1.header('Input')

    c2.header('Description')
    c2.info(Descriptions.PREPROCESSING_ABOUT)
    c2.error(Descriptions.PREP_INPUT)
    c2.success(Descriptions.PREP_OUTPUT)

    upload = c1.file_uploader("Upload Dataframe", type=["csv"])

    if (upload is not None):
        data = pd.read_csv(upload, encoding= 'unicode_escape').iloc[: , 1:]
        if (data is not None):
           return data

def handle(data):

    """
    handle(data) applies the preprocessing funct.
    defined.

    param data: uncleaned data
    return df: cleaned data
    """

    st.markdown('---')
    st.markdown('## Data Cleaning')

    columns_drop_nan = st.multiselect("Which columns do you want to drop NaN Values?", data.columns)
    columns_encode = st.multiselect("Which columns do you want to encode categorical values?", data.columns)
    flag_names = st.text_area("What should be the name of the flag columns?")

    map = st.text_area("Which columns would you like to rename?", help = "Please enter text just like a Python dictionary: { oldColumnName1: newColumnName1, oldColumnName2: newColumnName2, ..., oldColumnNameN: newColumnNameN}")
    
    # Transformation
    trans_column = st.selectbox("Which columns do you want to transform their dtype?", data.columns)
    transform_options = ['Integer', 'Float', 'String']
    transform_to = st.selectbox("Which columns do you want to transform their dtype?", transform_options)
    
    if st.button("Apply Changes"):

        data = preProcess.drop(data, columns_drop_nan)
        data = preProcess.fill(data)

        flag_columns_names = flag_names.split(',')
        df = preProcess.createFlag(data, columns_encode, flag_columns_names)

        map_to_dict = ast.literal_eval(map)
        # st.write(map_to_dict)
        df = df.rename(columns=map_to_dict)

        df = transform(df, trans_column, transform_to)

        st.success('Data cleaned!')
        return df
    
def transform(data, column, type):

    """
    transform(....) transforms dtype of columns.

    :param data: dataframe
    :param column: select column
    :param type: target dtype

    :return transformed df
    """

    if (type == 'Integer'):
        data[column] = data[column].astype(int) 
    if (type == 'Float'):
        data[column] = data[column].astype(float) 
    if (type == 'String'):
        data[column] = data[column].astype(str) 
    return data

def display_data(data):

    """
    display_data(data) visualizes the input dataframe.
    """
    st.markdown('---')
    st.markdown('## Data Overview')
    st.write(data)

def run_diagnostics(data):

    """
    run_diagnostics(data) visualizes the analysis from 
    "missing_zero_values_table(....)"
    """

    st.markdown('---')
    st.markdown('## Data Diagnostics')
    diag = missing_zero_values_table(data)
    st.table(diag)

    fig = px.histogram(diag, y="Data Type", color=diag.index)
    fig_two = px.histogram(diag, x = diag.index, y="Missing Values")
    
    c1, c2 = st.columns((1, 1))
    c1.markdown('#### Data Type')
    c1.plotly_chart(fig)

    c2.markdown('#### NaN Values per Column')
    c2.plotly_chart(fig_two)

"""
Credit to: https://stackoverflow.com/questions/26266362/
how-to-count-the-nan-values-in-a-column-in-pandas-dataframe

This function goes through each column and creates a summary
of important attributes. """

def missing_zero_values_table(df):
        zero_val = (df == 0.00).astype(int).sum(axis=0)
        mis_val = df.isnull().sum()
        mis_val_percent = 100 * df.isnull().sum() / len(df)
        mz_table = pd.concat([zero_val, mis_val, mis_val_percent], axis=1)
        mz_table = mz_table.rename(
        columns = {0 : 'Zero Values', 1 : 'Missing Values', 2 : '% of Total Values'})
        mz_table['Total Zero Missing Values'] = mz_table['Zero Values'] + mz_table['Missing Values']
        mz_table['% Total Zero Missing Values'] = 100 * mz_table['Total Zero Missing Values'] / len(df)
        mz_table['Data Type'] = df.dtypes.astype(str)
        mz_table = mz_table[
            mz_table.iloc[:,1] != 0].sort_values(
        '% of Total Values', ascending=False).round(1)
        st.info("Your selected dataframe has " + str(df.shape[1]) + " columns and " + str(df.shape[0]) + " Rows.\n"      
            "There are " + str(mz_table.shape[0]) +
              " columns that have missing values.")
        return mz_table



