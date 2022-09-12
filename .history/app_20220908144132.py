# Dependencies
import streamlit as st
import home
import research_page
import videos_page
import model.mdp_solver as genSolver
import model.preprocessing as prepProcess
import model.states as custSegm
import model.transitions_probabilities as custDyn
import model.mcp_solver as solveCamp
import model_dependencies.google_sheet as db
import model.rewards as car

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
        self.features = ['Home Page', 'Preprocessing', '1. States', '2. Transitional Probabilities', '3. Transitional Rewards', '4. MDP Solver', '5. Marketing Campaign Planner', 'Simulation History', 'Documentation', 'Videos']
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

        # CUSTOMER DYNAMICS
        if self.page == self.features[3]:
            custDyn.display_customer_dynammics()

        # REWARDS
        if self.page == self.features[4]:
            car.display_input_rewards_actions()

        # MDP SOLVER PAGE
        if self.page == self.features[5]:
            genSolver.solver()

        # CAMPAIGN PLANNER PAGE
        if self.page == self.features[6]:
            solveCamp.display_campaing_planner_page()
            
        # SIMULATION HISTORY PAGE
        if self.page == self.features[7]:
            db.display_simulation_history()

         # DOCUMENTATION PAGE
        if self.page == self.features[8]:
            research_page.display_research_page()

        # VIDEOS PAGE
        if self.page == self.features[9]:
            videos_page.display_video_page()
            
# Initiating class
route = Router()

# Displaying Sidebar Structure
home.sidebar.sidebar_functionality()
route.display_router()
home.sidebar.sidebar_contact()
route.route()