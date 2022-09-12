# Dependencies
import streamlit as st
import home
import model.preprocessing as prepProcess
import model.states as custSegm
import model.transitions_probabilities as custDyn

st.set_page_config(
     page_title="Ex-stream-ly Cool App",
     page_icon="🧊",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://www.extremelycoolapp.com/help',
         'Report a bug': "https://www.extremelycoolapp.com/bug",
         'About': "# This is a header. This is an *extremely* cool app!"
     }
 )

# <<     FEATURE: ROUTER       >>
# Here I define everything related
# to controlling a user through his 
# user experience
class Router:

    # Router attributes
    def display_router(self):
        self.features = ['Home Page', 'Preprocessing', '1. States']
        self.page = st.sidebar.selectbox('Select Page', self.features)
        st.sidebar.markdown('---')

    # Router routing
    def route(self):

         # HOME PAGE
        if self.page == self.features[0]:
            home.display_home()

        #  PREPROCESSING PAGE
        if self.page == self.features[1]:
            prepProcess.display_preprocessing()

        # CUSTOMER SEGMENTATION
        if self.page == self.features[2]:
            custSegm.display_customer_segmentation()
            
# Initiating class
route = Router()

# Displaying Sidebar Structure
home.sidebar.sidebar_functionality()
route.display_router()
home.sidebar.sidebar_contact()
route.route()