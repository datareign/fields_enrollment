import streamlit as st
import pandas as pd
import datetime
from google.cloud import firestore
from google.oauth2 import service_account
import json
from params import *
import uuid
import base64
import streamlit_authenticator as stauth
from google.cloud import storage
import io
import folium
from streamlit_folium import st_folium

st.set_page_config(layout="wide")


#env='prod'
env='dev'

key_dict=json.loads(st.secrets['textkey'])
creds=service_account.Credentials.from_service_account_info(key_dict)
db=firestore.Client(credentials=creds,project='agdata-f5a79')

st.title('ProGro Consulting, Inc.')
st.subheader('Mark fields for enrollment.')


col0,col1=st.columns((2,1))
options=['Broadcast Fertilizer','Starter Fertilizer','Seeding','Other']
with col0:
    '''
    Using the map below, navigate to a field of interest and add a pop up
    to the approximate center of the field by clicking your left mouse button. 
    It will show values for Latitude and Longitude. Next fill out the data 
    fields and submit. It is important to provide details on whether or not
    to include pivot corners or other factors impacting how boundaries are
    drawn. To add additional fields, navigate to them, add a popup, and 
    modify data fields as needed.
    '''
    
    m=folium.Map(location=[39,-100],zoom_start=4)
    BASEMAPS['Google Satellite Hybrid'].add_to(m)
    popup=folium.LatLngPopup()
    m.add_child(popup)
    st_data=st_folium(m,width=1000,height=500)
    
with col1:
    if 'df' not in st.session_state:
        st.session_state.df=pd.DataFrame(columns=[])
    client=st.text_input('Client')
    farm=st.text_input('Farm')
    field=st.text_input('Field')
    option=st.selectbox('Type',options)
    prev_crop=st.text_input('Previous Crop')
    targ_crop=st.text_input('Target Crop')
    notes=st.text_area('Notes')
    uid=str(uuid.uuid4())
    now=datetime.datetime.utcnow()
    if st_data['last_clicked']!=None:
        y=st_data['last_clicked']['lat']
        x=st_data['last_clicked']['lng']
        data_dict={'log_datetime':now,
                             'uuid':uid,
                             'client':client,
                             'farm':farm,
                             'field':field,
                             'type':option,
                             'prev_crop':prev_crop,
                             'targ_crop':targ_crop,
                             'x':x,
                             'y':y,
                             'notes':notes}
        if st.button('SUBMIT'):
            st.session_state.df=pd.concat([st.session_state.df,
                                           pd.DataFrame([data_dict])],ignore_index=True)
            doc_ref=db.collection(f'targ_fields_{env}').document(f'{uid}')
            doc_ref.set(data_dict)
            st.success(f'You have successfully submitted {client} {farm} {field}.')
            
with col0:
    df_cols_display=['client','farm','field','type','prev_crop','targ_crop']
    if len(st.session_state.df)>0:
        st.dataframe(st.session_state.df[df_cols_display])