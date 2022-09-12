import pandas as pd
import streamlit as st
import model_dependencies.segmentation_dependecy as segmentRevolver

from inform import Descriptions

def display_customer_segmentation():

    st.title("Clustering")
    st.markdown('---')

    data = select_user_journey()

    if (data is not None):

        # Display Data
        display_data_being_used(data)

        # CART Targets
        target_dict = define_cart_targets(data)

        if (target_dict is not None):
            # Running CART
            apply_cart(data, target_dict)
            # st.write(snippet)
        
        else:
            st.warning('Waiting to press the Submit Button!')

    else: 
        st.markdown('---')
        st.warning('Before we start, you need to feed the algorithm some data!')

def select_user_journey():

    upload = st.file_uploader("Upload Dataframe", type=["csv"], key='competitor_data')
    #data = pd.read_csv("data/datasets/dummy/cart/weatherAUS 3.csv")

    if (upload is not None):
        data = pd.read_csv(upload).iloc[: , 1:]
        return data