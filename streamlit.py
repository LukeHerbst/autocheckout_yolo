import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import cv2
import sqlite3
import database as db
import data
import computer_vision as v
import time
from streamlit.server.server import Server
#Initialize everything
net = v.model_net(data.MODEL, data.WEIGHT)
connection = sqlite3.connect('store.db')
cursor = connection.cursor()
db.create_or_connect_database(cursor)
label_keeper = []
chips_prod, milk_prod, oreo_prod,snickers_prod,sting_prod = db.create_and_save_current_products(connection,cursor)
prod_dict = {'milk': milk_prod,'oreo':oreo_prod,'sting':sting_prod,'snickers':snickers_prod,'chips':chips_prod}
current_cust_id = 0


######################
menu = ['Customers', 'Shop Dashboard']
choice = st.sidebar.selectbox('Pages', menu)


# st.form_submit_button(label: str = 'Submit', help: Optional[str] = None) → bool coluld i use this ?? 

if choice == 'Customers':
    st.header('Auto Checkout')
    form0 = st.form('my_form0')
    status = form0.selectbox('Select',['select option','new_customer','existing_customer'])
    submitted0 = form0.form_submit_button("Submit_choice")
    #customer sign_in
    
    if status == 'new_customer':
        form1 = st.form('my_form1')
        name = form1.text_input("Name")
        email = form1.text_input("email")
        phone =form1.text_input("phone")
        submitted1 = form1.form_submit_button("Submit_new_customer_details")
        if submitted1:
            current_cust  = db.Customer(name,email, phone)
            current_cust.save_to_db(connection,cursor)
            st.write(current_cust)
            current_cust_id = current_cust.customer_id
    
    elif status == 'existing_customer':
        form2 = st.form('my_form2')
        email = {'email':form2.text_input("what is your email address ?")}
        submitted2 = form2.form_submit_button("Submit_email")
        if submitted2 and (len(email['email']) > 4):
            current_cust_id = db.find_sign_in_customer_id(cursor,email)
            
    st.write(f"the customer id is {current_cust_id}")
    #order creation
    if current_cust_id > 0:
        current_order = db.create_order(current_cust_id,connection, cursor)
        st.write(f'the current order id  is {current_order.order_id}, for customer {current_cust_id} ')
        st.write('ready for webcam')
        st.write(f'{current_order.date_time}')
    #st.write(f"currentorder is here {current_order}")  #debugging
    st.title("Webcam Live Feed")
    st.text('place your items then open the webcam and wait 5 seconds')
    
    
    opener = st.button("open video camera")

    @st.cache(allow_output_mutation=True)
    def get_cap():
        return cv2.VideoCapture(0,cv2.CAP_DSHOW)
    
    
    if opener:
        cap = get_cap()
        
    
    # closer = st.button("close video camera",key= 2)
    # if closer:
    #         cap.close()          
       
    stframe = st.empty()
       
    start_time = time.time() 
    #st.write(f"current order is here {current_order}")  #debugging
    while cap.isOpened():       
        
        
        ret, frame = cap.read()
        # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        #process image
        img_processed =  cv2.resize(frame,(data.IMG_WIDTH,data.IMG_HEIGHT),cv2.INTER_AREA)
        #model forward pass
        boxes , confidences, class_ids, indexes = v.forwardpassoutput(img_processed,net,data.IMG_WIDTH,data.IMG_HEIGHT)
        
        result = img_processed.copy()
        if len(indexes) > 0:
            result ,label_keeper = v.draw_boxes( result, boxes , confidences, class_ids, indexes,data.classes_name,data.colors,data.font)
        
        stframe.image(result, channels="BGR") # 
        stop = time.time() - start_time
        #st.write(f"currentorder is here {current_order}")  #debugging
        if stop >= 5 :
            cap.release()
            break
       
    st.write(f"currentorder is here {current_order}")  #debugging    
    purchase_list , total_bill = v.receipt_writer(label_keeper,data.items_prices)

    for i in range(len(label_keeper)):
        st.write(purchase_list[i])
    st.write(total_bill)  
    db.create_order_items(label_keeper,current_order,prod_dict,connection,cursor) 
    st.write(f"currentorder is here {current_order}")  #debugging
    
elif choice == 'Shop Dashboard':
    st.header("Shop Dashboard")   
    
    chosen_query = st.selectbox("choose a query",list(data.query_dictionary.keys()))
    # @st.cache(hash_funcs={sqlite3.Connection:'my_hash_func'})
    def get_dataframe():
        return st.dataframe(db.sql_query(data.query_dictionary[chosen_query],connection))
    
    get_dataframe()

