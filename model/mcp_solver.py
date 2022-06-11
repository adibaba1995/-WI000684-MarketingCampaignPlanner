# Dependencies
import streamlit as st
import numpy as np
import pandas as pd
from numpy.linalg import matrix_power
import csv
from random import sample
from inform import Descriptions
import plotly.graph_objects as go
import plotly.express as px
import model_dependencies.google_sheet as googleSheet

def display_campaing_planner_page():
    """
    display_campaing_planner_page(...) bring all page-related
    functionality together and render all results
    """ 

    st.title('Marketing Campaign Planner')
    st.markdown('---')

    c1, c2 = st.columns((2, 1))
    c1.header('Input')

    c2.header('Description')
    c2.info(Descriptions.CAMPAIGN_PLANNER_ABOUT)
    c2.error(Descriptions.CAMPAIGN_PLANNER_INPUT)
    c2.success(Descriptions.CAMPAIGN_PLANNER_OUTPUT)

    # Option to decide whether or not to use data generated by us
    data_options = ['Import own data', 'Use data collected by authors']
    option = c1.radio('Which data would you like the model to consider?', data_options)
    
    if (option == data_options[0]):
        
        # TRANSITION PROBABILITIES
        upload_transition = c1.file_uploader("Upload Dataframe", type=["csv"], key = 'trans_upload_key')
        
        # OPTIMAL POLICY
        upload_optimal_policy = c1.file_uploader("Upload Dataframe", type=["csv"], key = 'policy_upload_key')

        # PERIODS
        periods = int(c1.number_input('Insert the number of periods to be consider', value = 12, step = 1))

        # SIMULATIONS
        simulations = int(c1.number_input('Insert the number of simulations to be consider', value = 1, step = 1))

        if (upload_transition is not None and upload_optimal_policy is not None):
            
            # Desired DF Shape
            transition_probabilities = pd.read_csv(upload_transition).iloc[: , 1:]
            optimal_policy = pd.read_csv(upload_optimal_policy).iloc[: , 1:]

            # STATES 
            # states_df = pd.DataFrame(transition_probabilities[['state', 'state_category', 'follow_up_state', 'follow_up_state_category']])
            states_intermediary = transition_probabilities.groupby(['state', 'state_category']).count().reset_index()
            states_df = pd.DataFrame(columns=['States', 'States Category'])
            states_df['States'] = states_intermediary['state']
            states_df['States Category'] = states_intermediary['state_category']

            # ACTIONS
            actions_df_intermediary = transition_probabilities.groupby(['action', 'action_category']).count().reset_index()
            actions_df = pd.DataFrame(columns=['Actions', 'Actions Category'])
            actions_df['Actions'] = actions_df_intermediary['action']
            actions_df['Actions Category'] = actions_df_intermediary['action_category']

            # Initial State
            initial_state = int(c1.selectbox('Insert the initial CLV State of the customer', states_df['States'].to_list()))

            # Overview all inputs for MCP Section
            display_all_inputs(transition_probabilities, states_df, actions_df, optimal_policy)

            # Solving the MCP 
            run_mcp_solver(states_df, actions_df, transition_probabilities, optimal_policy, periods, initial_state, simulations)

        else:
            st.markdown('---')
            st.warning('Before we start, you need to feed the algorithm some data!')

    # TODO: Visualize Rewards & Discount
    else:

        # PERIODS
        periods = int(c1.number_input('Insert the number of periods to be consider', value = 12, step = 1))

        # SIMULATIONS
        simulations = int(c1.number_input('Insert the number of simulations to be consider', value = 1, step = 1))

        # TRANSITION PROBABILITIES
        transition_probabilities = pd.read_csv('data/datasets/official/full_example/mcp_input.csv')

        # OPTIMAL POLICY
        optimal_policy = pd.read_csv('data/datasets/official/full_example/mcp_optimal_policy.csv')
    
        # STATES 
        # states_df = pd.DataFrame(transition_probabilities[['state', 'state_category', 'follow_up_state', 'follow_up_state_category']])
        states_intermediary = transition_probabilities.groupby(['state', 'state_category']).count().reset_index()
        states_df = pd.DataFrame(columns=['States', 'States Category'])
        states_df['States'] = states_intermediary['state']
        states_df['States Category'] = states_intermediary['state_category']

        # ACTIONS
        actions_df_intermediary = transition_probabilities.groupby(['action', 'action_category']).count().reset_index()
        actions_df = pd.DataFrame(columns=['Actions', 'Actions Category'])
        actions_df['Actions'] = actions_df_intermediary['action']
        actions_df['Actions Category'] = actions_df_intermediary['action_category']

        # Initial State
        initial_state = int(c1.selectbox('Insert the initial state category of the customer', states_df['States'].to_list()))

        # Overview all inputs for MCP Section
        display_all_inputs(transition_probabilities, states_df, actions_df, optimal_policy)

        # Solving the MCP 
        run_mcp_solver(states_df, actions_df, transition_probabilities, optimal_policy, periods, initial_state, simulations)

def display_all_inputs(transition_probabilities, states, actions, optimal_policy):
    st.markdown('---')
    st.markdown('## Inputs Overview')
    st.info("Here the user receives an overview of all inputs generated accross MCP's user experience: States, Actions, Rewards, Transition Probabilities and Optimal Policy.")

    c1, c2 , c3 = st.columns(3)

    c1.markdown('#### States')
    c1.write(states.drop(['States Category'], axis = 1))

    c2.markdown('#### Actions')
    c2.write(actions.drop(['Actions Category'], axis = 1))

    c3.markdown('#### Optimal Policy')
    states = states.sort_values(by=['States Category'])
    opt_policy = optimal_policy['action'].to_list()
    states['action'] = opt_policy
    # st.write(states)
    c3.write(states.rename(columns={"action": "Actions"}).drop(['States Category'], axis = 1))

    c4, c5 = st.columns(2)

    c4.markdown('#### Transition Probabilitites')
    c4.write(transition_probabilities.iloc[: , 1:].drop(['state_category', 'action_category', 'follow_up_state_category', "Reward (state, action, follow_up_state)"], axis = 1))

    c5.markdown('#### Rewards')
    c5.write(transition_probabilities.iloc[: , 1:].drop(['state_category', 'Probability Triple', 'action_category', 'follow_up_state_category'], axis = 1))


def run_mcp_solver(states, actions, transition_probabilities, optimal_policy, periods, initial_state, simulations):

    """
    run_mcp_solver(...) is the algorithm that apply the respective optimal 
    action based on the current state of the customer over the number of 
    decision periods and in number of simulations.
    
    :param states: set states
    :param actions: set actions
    :param transition_probabilities: transition probabilities & rewards combined
    :param optimal_policy: optimal policy from MDP
    :param periods: enumber of decision periods
    :param initial_state: customer initial state
    :param simulations: number of simulations

    """

    st.write('---')
    st.write('## Marketing Campaign over {} Simulations Result'.format(simulations))
    st.info('Here N simulations are calculated using the inputs of MCP. The user sees below a summary table as well as some visualizations.')

    matrix_prob = input_to_probability_matrix(transition_probabilities, len(actions), len(states))
    
    # [CURRENT STATE] Here I optimize UX by providing him the real
    # CLV state, e.g. 50, then I encode back to {1, 2, ..., N} such that 
    # it fits the optimal campaing planner algorithm in apply_optimal_policy(....)
    intermediary_state_variable = 0
    state_map = dict([(i,[a]) for i, a in zip(states['States'], states['States Category'])])
    user_state_selection = initial_state
    for key in state_map:
        if (key == user_state_selection):
            intermediary_state_variable = state_map.get(key)

    current_state = intermediary_state_variable[0]
    #st.write(current_state)

    states = states.sort_values(by=['States Category'])
    opt_policy = optimal_policy['action'].to_list()
    states['action'] = opt_policy

    opt_to_map = states.copy()
    action_cat = optimal_policy["action_category"]
    opt_to_map["action_category"] = action_cat 
    
    # st.write('Opt Map')
    # st.write(opt_to_map)

    # [MAPs]  Maps to encode categories
    optimal_states_cat_to_action_cat_map = dict([(i,[a]) for i, a in zip(opt_to_map['States Category'], opt_to_map['action_category'])])
    optimal_state_cat_to_state_map = dict([(i,[a]) for i, a in zip(opt_to_map['States Category'], opt_to_map['States'])])
    optimal_action_cat_to_action = dict([(i,[a]) for i, a in zip(opt_to_map['action_category'], opt_to_map['action'])])

    # SIMULATIONS

    # Action Control Structure 
    action_storage = []
    state_storage = []

    for s in range(simulations):

        action_simulation_number = []
        state_transition = []

        delta_clv_count = 0
    
        counter = 0
        while counter < periods:
            
            current_action = optimal_states_cat_to_action_cat_map.get(current_state)[0]
            action_simulation_number.append(current_action)
        
            prob_matrix_current = matrix_prob[current_action]
            # c1.write('[START] For period {} the state is {} and the matrix considered is {}'.format(count, current_state, current_action))
            # c1.write(prob_matrix_current)

            random_sample = sample(list(enumerate(sorted(prob_matrix_current[current_state]))), 1)
            current_state = random_sample[0][0]
            state_transition.append(current_state)
            # if (count == 0):
            #     c1.write('[END] For period {} the follow up state is {} with prob. of {} from sample {}'.format(count, current_state, random_sample[0][1], random_sample,0))
            # else:
            #     c1.write('[END] For period {} the follow up state is {} with prob. of {} from sample {}'.format(count, current_state, random_sample[0][1], random_sample, 0))

            # c1.markdown('---')

            counter = counter + 1        

        action_storage.append(action_simulation_number)
        state_storage.append(state_transition)
            
        # # [FORMATING RESULT -> RESULT DATAFRAME]
        campaign_df = pd.DataFrame(state_storage[s], columns = ["States"])
        campaign_df['Period'] = campaign_df.index
        campaign_df['Period'] = campaign_df['Period'].apply(lambda x: x + 1)
        first_column = campaign_df.pop('Period')
        campaign_df.insert(0, 'Period', first_column)

        campaign_df = campaign_df.replace({"States": optimal_state_cat_to_state_map})
        campaign_df['Best Actions'] = action_storage[s]
        
        campaign_df = campaign_df.replace({"States": optimal_state_cat_to_state_map})

        # Total cost of Actions
        cost_action_map = dict([(i,[a]) for i, a in zip(transition_probabilities['action_category'], transition_probabilities['cost'])])
        campaign_df['Costs'] = campaign_df['Best Actions']
        campaign_df = campaign_df.replace({"Costs": cost_action_map})
        campaign_df = campaign_df.replace({"Best Actions": optimal_action_cat_to_action})

        # Delva CLV
        clvs = campaign_df['States'].to_list()
        delta_clv = clvs[len(clvs) - 1]- clvs[0]
        delta_clv_count = delta_clv_count + delta_clv

        # c1.markdown('#### Result Table')
        # c1.table(campaign_df)

        # simulation_backlog['Marketing Campaign'] = campaign_df['Best Actions'].to_list()

        # st.write(simulation_backlog)

        # st.write(state_transition)
        # st.write(action_storage)

        # c1.write('[END] In Simulation Number {}'.format(s))

    # st.write(action_storage)
    # st.write(state_storage)

    list_summary = ['Period']

    for a in range(len(actions['Actions'].to_list())):
        list_summary.append(actions['Actions'].to_list()[a])

    summary_df = pd.DataFrame(columns = list_summary)

    for c in range(len(list_summary)):
        zeros = np.zeros(periods)
        summary_df[list_summary[c]] = zeros

    summary_df['Period'] = summary_df.index
    summary_df['Period'] = summary_df['Period'].apply(lambda x: x + 1)

    for y in range(len(action_storage)):
        intermediary = pd.DataFrame(action_storage[y], columns = ['Best Actions']).replace({"Best Actions": optimal_action_cat_to_action})
        for z in range(periods):
            for x in range(1, len(summary_df.columns)):
                if (intermediary['Best Actions'][z] == summary_df.columns[x]):
                   summary_df[summary_df.columns[x]][z] = summary_df[summary_df.columns[x]][z] + 1
            
    
    summary_df = summary_df.apply(lambda x: x * 1/simulations)
    summary_df['Period'] = summary_df['Period'].apply(lambda x: x * simulations).astype(int)

    summary_df = summary_df.drop(['Period'], axis = 1)
    summary_df['Overall Best Action'] = summary_df.idxmax(axis=1)
    summary_df['Period'] = summary_df.index
    summary_df['Period'] = summary_df['Period'].apply(lambda x: x + 1)

    summary_df.insert(0, 'Period', summary_df.pop('Period'))

    cost_action_name_map = dict([(i,[a]) for i, a in zip(transition_probabilities['action'], transition_probabilities['cost'])])
    summary_df['Cost Overall Best Action'] = summary_df['Overall Best Action']
    summary_df = summary_df.replace({"Cost Overall Best Action": cost_action_name_map})

    for u in range(len(state_storage)):
        intermediary_clv = pd.DataFrame(state_storage[u], columns = ['Average CLV Change']).replace({"Average CLV Change": optimal_state_cat_to_state_map})
        for v in range(periods - 1):
                intermediary_clv['Average CLV Change'][v] = intermediary_clv['Average CLV Change'][v] + state_storage[u][v + 1] - state_storage[u][v]

    av_start_end = 0
    for q in range(len(state_storage)):
        intermediary_clv_two = pd.DataFrame(state_storage[q], columns = ['CLV']).replace({"CLV": optimal_state_cat_to_state_map})
        # st.write(intermediary_clv_two['CLV'][periods-1])
        av_start_end = av_start_end + intermediary_clv_two['CLV'][periods-1]

    av_start_end = (av_start_end / simulations) - state_storage[0][0]
    # st.write(av_start_end)

    intermediary_clv['Average CLV Change'] = intermediary_clv['Average CLV Change'] .apply(lambda x: x * 1 / simulations)
    result = pd.concat([summary_df, intermediary_clv], axis=1)

    overall_action_set = result['Overall Best Action'].to_list()
    # st.write(overall_action_set)

    result = result.drop(['Period', 'Overall Best Action'], axis = 1)

    averages = result.mean(axis = 0)
    # st.write(averages)

    total_cost = result['Cost Overall Best Action'].sum()

    result['Overall Best Action'] = overall_action_set
    result['Period'] = result.index
    result['Period'] = result['Period'].apply(lambda x: x + 1)

    result = result.reindex(columns=['Period','agent', 'call', 'email', 'mail', 'no contact', 'tv', 'Overall Best Action', 'Cost Overall Best Action'])
    
    st.markdown('#### Table Summary')
    st.write(result)
    st.download_button(
        "Download Statistics",
        convert_df(result),
        "statistics.csv",
        "text/csv",
        key='stats-csv'
    )

    st.markdown('#### Averages')
    avg_index = averages.index.tolist()
    avg_values = averages.to_list()
    # st.write(avg_values)

    c3, c4, c5, c6, c7, c8, c9, c10, c11 = st.columns([1,1,1,1,1,1,1,1,2])
    avg_cols = [c3, c4, c5, c6, c7, c8, c9, c10]

    for m in range(len(avg_index)):
        avg_cols[m].metric(avg_index[m].title(), round(avg_values[m], 3))

    c11.metric(label="Total Cost of Overall Best Campaign", value = round(total_cost, 3))
    st.download_button(
    "Download Averages",
    convert_df(averages),
    "averages.csv",
    "text/csv",
    key='averages-csv'
    )

    st.markdown('---')
    st.markdown('## Visualizations')
    c15, c16, c17 = st.columns(3)

    plot3d = go.Figure(data=[go.Surface(x = result['Period'], z =result[['agent', 'call', 'email', 'mail', 'no contact', 'tv']])])
    plot3d.update_layout(title='Action Distribution over Periods', autosize=False,
                width=500, height=500)
    c15.plotly_chart(plot3d)  

    pie = px.pie(values=avg_values[0:5], names= avg_index[0:5])
    pie.update_traces(textposition='inside')
    pie.update_layout(title='Average Action (%)', autosize=False, uniformtext_minsize=12, uniformtext_mode='hide', width=500, height=500)      
    c16.plotly_chart(pie)

    hist = px.histogram(result, x= 'Overall Best Action')
    hist.update_layout(title='Average Action Distribution', autosize=False, width=500, height=500 )
    c17.plotly_chart(hist)

    # Store Run
    store_run(simulations,	initial_state,	avg_values[0], avg_values[1], avg_values[2], avg_values[3], avg_values[4], 	avg_values[5], 	avg_values[6], 	avg_values[7], total_cost)

def store_run(simulations,	initial_state,	agent_average,	call_average, email_average, mail_average, no_contact_average, tv_average, cost_overall_best_action, average_clv_change, total_cost_of_overall_best_campaign):
    
    """
    store_run(...) stores a MCP run in our Database which is 
    a google sheet (see google_sheet.py)

    :param simulations: MCP Number simulations
    :param initial_state: MCP initial state
    :param agent_average: Average Agent Appearances
    :param call_average: Average Call Appearances
    :param email_average: Average Email Appearances
    :param mail_average: Average Mail Appearances
    :param no_contact_average: Average No Contact Appearances
    :param tv_average: Average TV Appearances
    :param cost_overall_best_action: Cost Overall Best Action
    :param average_clv_change: Average CLV Change
    :param total_cost_of_overall_best_campaign: Total Cost of Overall Best Campaign
    """ 
    
    store = ['Dont Share', 'Share Simulation']
    store_choice = st.radio('Let the world know about this Simulation', store)

    if (store_choice == store[0]):
        st.error('Why not let the world benefit from your simulation ? :O')
    else:
        googleSheet.save_simulation(simulations,initial_state, agent_average, call_average, email_average, mail_average, no_contact_average, tv_average, cost_overall_best_action, average_clv_change, total_cost_of_overall_best_campaign)
        st.success('Success!')
  
def display_matrix_probability(path):

    """
    display_matrix_probability(...) reads in the
    .csv file stored at given path.

    :param path: string containing the location of file
    :return: dataframe of transition probabilities
    """ 

    st.markdown('---')
    st.write('## Matrix Probability Overview')

    results = []
    with open(path) as csvfile:
        reader = csv.reader(csvfile, quoting=csv.QUOTE_NONNUMERIC)
        for row in reader:
            results.append(row)

    matrix_prob = np.matrix(results)

    return matrix_prob

def input_to_probability_matrix(data, number_actions, number_states):

    """
    input_to_probability_matrix(...) transforms the dataframe of
    transition prob. into a list of matrices for each action.

    :param data: Trans. Probabilitites Dataframe
    :param number_actions: Number Actions
    :param number_states: Number of States

    :return: List of Matrices
    """ 

    # Probability Matrix
    transition_matrices = []

    for i in range(number_actions):

        action_transition_matrix = np.zeros((number_states,number_states))

        for j in range(number_states):
            for h in range (number_states):

                coordinate = (j, i, h)

                for l in range (len(data.index)):
                    cooperator = (data['state_category'][l], data['action_category'][l], data['follow_up_state_category'][l])

                    if (cooperator[0] == coordinate[0] and cooperator[1] == coordinate[1] and cooperator[2] == coordinate[2]):
                        action_transition_matrix[j][h] = data['Probability Triple'][l]

        transition_matrices.append(action_transition_matrix)

    return transition_matrices

def calculate_probability_distributions(matrix_prob, current_state, periods, action):

    """
    calculate_probability_distributions(...) calculates the 
    probability distributions for every state for every given 
    period.

    :param matrix_prob: transition probabilities from Customer Dynammics
    :param current_state: initial state of customer
    :param periods: number of periods
    :param action: list of possible actions

    :return: 3D list containing the state probabilities, List of optimal actions
    """ 

    #st.write('---')
    #st.write('## Calculating Probability Distributions')

    num_rows, num_cols = matrix_prob.shape

    init_vector = np.zeros(num_rows)
    init_vector[current_state - 1] = 1

    state_vector = list()
    state_vector.append(init_vector.reshape((1, 3)))

    for j in range(1, periods):
        result = np.zeros(num_rows) 

        result = np.matmul(state_vector[0].reshape((1, 3)), matrix_power(matrix_prob, j))
    
        state_vector.append(result)

    # st.write(state_vector)

    for i in range(len(state_vector)):
        state_vector[i] = np.array(state_vector[i])

    # st.write(state_vector)

    max_values = np.zeros(periods)
    campaign = ""

    for h in range(periods):

        count = 0
        for k in range(num_cols):
            if (state_vector[h][0][k] > max_values[h]):
                # st.write('New Max {}'.format(state_vector[h][0][k]))
                max_values[h] = state_vector[h][0][k]
                count = k

                # st.write('Count {} and Action {}'.format(count, action[count]))
            
        campaign = campaign + "," + action[count]
                
    campaign_recommendation = campaign.split(",")
    campaign_recommendation.pop(0)
    
    #st.write('Corresponding Marketing Campaign {}'.format(campaign_recommendation))
    return state_vector, campaign_recommendation

def get_state_vector_coeffiecients(state_vector, periods, num_cols):

    """
    get_state_vector_coeffiecients(...) reduces the dimensionality of
    state_vector datastructure to 2d datastructure.

    :param state_vector: 3D datastructure
    :param periods: number of periods
    :param num_cols: number of states
    :return: 2D list containing the state probabilities
    """ 

    vector_coefficients = np.zeros((periods, num_cols))

    for h in range(periods):
            for k in range(num_cols):
                vector_coefficients[h][k] = state_vector[h][0][k]

    #st.write(vector_coefficients)

    return vector_coefficients 

def display_overview(periods, states, state_vectors_prob, campaign_recommendation):

    """
    display_overview(...) creates the final table of results.
    It provides an overview of all best actions for all periods,
    given the state probabilities

    :param periods: number of periods
    :param states: number of states
    :param state_vectors_prob: 2D data structure containing probabilities
    :param campaign_recommendation: list with optimal actions
    """ 

    st.write('---')
    st.write('## Marketing Campaign Recommendation')

    c1, c2 = st.columns((1, 1))

    period_values = list(range(1, periods + 1))

    overview_df = pd.DataFrame(state_vectors_prob, columns = states, dtype = float)
    # overview_df["Period"] = period_values
    overview_df.insert(loc = 0, column = "Period", value = period_values)
    overview_df.insert(loc = len(states) + 1, column = "Best Action", value = campaign_recommendation)

    overview_df.reset_index(drop=True, inplace=True)

    style = overview_df.style.hide_index()
    c1.write(style.to_html(), unsafe_allow_html=True)

    c2.header('Result')
    c2.success('The policymaker should apply  the following market campaign {} for the upcoming {} months.'.format(campaign_recommendation, periods))
    # st.table(overview_df)
        
def display_data(data):

    """
    display_data_being_used(...) displays the data

    :param data: dataframe of data
    """ 

    st.markdown('---')
    st.write('## Data Overview')
    st.write(data)

@st.cache
def convert_df(df):

   """
   convert_df(...) convert df to csv
   
   :return: csv file
   """

   return df.to_csv().encode('utf-8')