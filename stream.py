import streamlit as st
from gmail import *
user_id = 'me' # change 'me' with email address for commercial use.
service = get_service()

def output_data(function):
    i = 1
    for _ in function:
        st.write("Email ", i)
        i += 1
        st.write(_)
        st.write("**************")
def check_option():
    option = st.selectbox(
     'Select Function',
     ('Select a Function','Get All Emails', 'Get All Senders Data'))
    if option == 'Get All Emails':
        output_data(get_all_emails(service,user_id))
    elif option == 'Get All Senders Data':
        output_data(get_all_senders_data(service,user_id))


check_option()

