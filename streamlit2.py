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

CUSTOMER_ID = 0 


def sql_connect():
    connection = sqlite3.connect("store.db")
    
    return connection

def sql_cursor(connection):
    cursor = connection.cursor()
    return cursor 

def sidebar():
  
    menu = ["Customers", "Dashboard"]
    choice = st.sidebar.selectbox("Pages", menu)

    return choice 

def form(name,email,phone,cursor,connection):
    current_customer = db.Customer(name,email,phone)
    current_customer.save_to_db(connection,cursor)
    return current_customer.customer_id
def form_exist(cursor,email):
    customer_id = db.find_sign_in_customer_id(cursor,email)
    return customer_id


def customers(cursor,connection):
    customer_id = 0
    st.header("Auto checkout")

    form_0 = st.form("Form")
    status = form_0.selectbox(
        "Select", ["Select Option", "New Customer", "Existing Customer"]
    ) 
    submitted_0 = form_0.form_submit_button("Submit Choice")

    if status == "New Customer":
        form_1 = st.form("Form 1")    
        name = form_1.text_input("Name")
        email = form_1.text_input("Email")
        phone = form_1.text_input("Phone")
        form_1.write('place all your items in the square then submit')
        submitted_1 = form_1.form_submit_button("Submit new customer details")        
        if submitted_1:
            customer_id = form(name,email,phone,cursor,connection)
   
    elif status == 'Existing Customer':
        form2 = st.form('my_form2')
        email = {'email':form2.text_input("what is your email address ?")}
        form2.write('place all your items in the square then submit')
        submitted2 = form2.form_submit_button("Submit_email")        
        if submitted2:
            customer_id = form_exist(cursor,email)
                    # st.write(f"the customer id is {customer_id}")
    
    return customer_id


@st.cache(hash_funcs={sqlite3.Cursor: id,sqlite3.Connection:id})
def product_saver(connection,cursor):
    chips_prod, milk_prod, oreo_prod,snickers_prod,sting_prod =  db.create_and_save_current_products(connection,cursor)
    return chips_prod, milk_prod, oreo_prod,snickers_prod,sting_prod


def camera():
    return cv2.VideoCapture(0, cv2.CAP_DSHOW)

if __name__ == "__main__":
    customer_id = 0
    connection = sql_connect()
    cursor = sql_cursor(connection)
    choice = sidebar()
    chips_prod, milk_prod, oreo_prod,snickers_prod,sting_prod = product_saver(connection,cursor) #db.create_and_save_current_products(connection,cursor) # should cache this 
    prod_dict = {'milk': milk_prod,'oreo':oreo_prod,'sting':sting_prod,'snickers':snickers_prod,'chips':chips_prod}
    net = v.model_net(data.MODEL, data.WEIGHT)
    label_keeper = []
    
    if choice == "Customers":
        customer_id = customers(cursor,connection)
    
    cap = None
    if customer_id > 0:
        st.write(f'your customer id is {customer_id} Happy shopping')
        current_order = db.create_order(customer_id,connection, cursor)
        cap = camera()
        stframe = st.empty()
        start_time = time.time() 
        stframe = st.empty()            
        
        while cap.isOpened(): 
            #st.write("Inside loop") 
            ret, frame = cap.read()
            img_processed =  cv2.resize(
                frame, (data.IMG_WIDTH,data.IMG_HEIGHT), cv2.INTER_AREA
            )
            
            boxes , confidences, class_ids, indexes = v.forwardpassoutput(img_processed,net,data.IMG_WIDTH,data.IMG_HEIGHT)
                
            result = img_processed.copy()
            if len(indexes) > 0:
                result ,label_keeper = v.draw_boxes(result, boxes , confidences, class_ids, indexes,data.classes_name,data.colors,data.font)
                
                                    
            stframe.image(result, channels="BGR")
            stop = time.time() - start_time
            
            
            
            if stop >= 7:
                cap.release()
                purchase_list , total_bill = v.receipt_writer(label_keeper,data.items_prices)
                st.write('Receipt')
                for i in range(len(label_keeper)):
                    st.write(purchase_list[i])
                st.write('total_bill',total_bill)
                st.write('GIVE YOUR MONEY TO LUKE')
                if total_bill > 0:  
                    db.create_order_items(label_keeper,current_order,prod_dict,connection,cursor) 
    
    elif choice == 'Dashboard':
        
        st.header("Shop Dashboard")   

        chosen_query = st.selectbox("choose a query",list(data.query_dictionary.keys()))
        # @st.cache(hash_funcs={sqlite3.Connection:'my_hash_func'})
        def get_dataframe():
            return st.dataframe(db.sql_query(data.query_dictionary[chosen_query],connection))

        get_dataframe()