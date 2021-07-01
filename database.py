# use this to keep all the database related functions 

import sqlite3
#from sqlite3.dbapi2 import Connection
import pandas as pd 
import datetime



def create_or_connect_database(cursor):
  #define a connection and a cursor 
  # connection = sqlite3.connect('store.db') # need to put these two lines in 

  # cursor = connection.cursor()

  # create the products table
  command1 = """ CREATE TABLE IF NOT EXISTS products (
          product_id INTEGER PRIMARY KEY AUTOINCREMENT, 
          name TEXT UNIQUE, 
          price INTEGER,
          quantity_in_stock INTEGER)
  """
  try:
      cursor.execute(command1)
  except Exception as err:
      print('ERROR AT CREATE  products TABLE', err)

  #create the customers table
  command2 =  """ CREATE TABLE IF NOT EXISTS customers(
          customer_id INTEGER PRIMARY KEY AUTOINCREMENT, 
          name   TEXT, 
          email   TEXT UNIQUE,
          phone   VARCHAR(255) UNIQUE)      
          """
  try:
      cursor.execute(command2)
  except Exception as err:
      print('ERROR AT CREATE customers TABLE', err)

  # create the orders table 
  command3 = """ CREATE TABLE IF NOT EXISTS orders(
          order_id INTEGER PRIMARY KEY AUTOINCREMENT, 
          customer_id  INTEGER, 
          date_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP ,        
          FOREIGN KEY(customer_id) REFERENCES customers (customer_id))
          """
  try:
      cursor.execute(command3)
  except Exception as err:
      print('ERROR AT CREATE orders TABLE', err)

  # create the order_item table
  command4 = """ CREATE TABLE IF NOT EXISTS order_item(
          item_id INTEGER PRIMARY KEY AUTOINCREMENT, 
          order_id INTEGER, 
          product_id  TEXT,
          quantity INTEGER,
          FOREIGN KEY(order_id) REFERENCES orders(order_id),
          FOREIGN KEY(product_id) REFERENCES products(product_id))
          """
  try:
      cursor.execute(command4)
  except Exception as err:
      print('ERROR AT CREATE order_item TABLE', err)
  
  #return connection , cursor
# connection = sqlite3.connect("store.db")
# cursor = connection.cursor()
# create_or_connect_database(cursor)

### this line needs to be used in the main.py to create/connect to db
#connection, cursor = create_or_connect_database()
# will deal with this tomorrow...

# function for new customers # i could also make the default be a guest ??? 
def new_customer(connection,cursor):
  """ A function to create a new customer"""  
  current_cust  = Customer(input("Name: "),input('email: '), input('Phone Number: '))
  current_cust.save_to_db(connection,cursor) 
  return  current_cust
#  
## use this line in the main.py to create a new_customer
#current_cust = new_customer()

#function for existing customers
def find_sign_in_customer_id(cursor,email):
    """This function uses the sqlite cursor and return the customer id using the inputted email  """
    #email = {'email':input("what is your email address? ")}
    query = """ SELECT customer_id FROM customers WHERE email = :email"""
    cursor.execute(query,email)
    id = cursor.fetchall()[0][0]
    return id 

### use this line in the main.py 
#current_customer_id = sign_in_customer(cursor)


#need to initialize these into my db at some point
def create_and_save_current_products(connection,cursor):
    """This function initializes our products into the db and return the product classes to be used in other parts of the program"""
    chips_prod = Product('chips',30000,100)
    crackers_prod = Product('crackers',18000,100)
    kitkat_prod = Product('kitkat',20000,100)
    milk_prod  = Product('milk', 33000,100)
    oreo_prod = Product('oreo',15000,100)
    pepsi_prod = Product('pepsi',12000,100)
    snickers_prod = Product('snickers',15000,100)
    sting_prod = Product('sting',12000,100)

    chips_prod.save_to_db(connection,cursor)
    crackers_prod.save_to_db(connection,cursor)
    kitkat_prod.save_to_db(connection,cursor)
    milk_prod.save_to_db(connection,cursor)
    oreo_prod.save_to_db(connection,cursor)
    pepsi_prod.save_to_db(connection,cursor)
    snickers_prod.save_to_db(connection,cursor)
    sting_prod.save_to_db(connection,cursor)
    return chips_prod, crackers_prod,kitkat_prod,milk_prod, oreo_prod,pepsi_prod,snickers_prod,sting_prod

# use this line in the main.py 
#chips_prod, milk_prod, oreo_prod,snickers_prod,sting_prod = create_and_save_current_products() need to run this in streamlit

def create_order(customer_id,connection,cursor):
  """A function to initialize an order"""  
  current_order = Order(customer_id)
  current_order.save_to_db(connection,cursor)
  
  return current_order

#this willl be used in the main.py somewhere 
##current_order = create_order(current_customer_id)


# this dictionary is needed to get the Product objects from the string produced in label_keeper

#prod_dict = {'milk': milk_prod,'oreo':oreo_prod,'sting':sting_prod,'snickers':snickers_prod,'chips':chips_prod}


def create_order_items(label_keeper,current_order,prod_dict,connection,cursor):
  """This function uses the label_keeper to create order_items,
   input them into order_items table in the db and update the quantity_in_stock in the products table of the db    """ 
  for label in label_keeper:
    temp_order  = Order_Item(current_order.order_id,prod_dict[label].product_id,1)  
    temp_order.save_to_db(connection,cursor)
    #update the quantity using these order items 
    prod_dict[label].decrease_quantity(temp_order.quantity,connection,cursor)
    
#use this line to create the orders this will be used in the main.py
#create_order_items(label_keeper)

#answer = input('Are you a new customer ? type yes or no')
# def get_customer_id(answer,cursor):    # I dont think I will be using this function anymore ???
#     """ A function to get sign in the customers into the 
#     db or connect to a current customers id the input should be yes or no"""
#     if answer == 'yes':
#         current_cust = new_customer()
#         current_customer_id = current_cust.customer_id
#     elif answer == 'no' :
#         current_customer_id = sign_in_customer(cursor)
#     else:
#         print('error with customer sign in: type yes or no')

# # once the customer is signed in we create the order:
#     if current_customer_id:
#         current_order = create_order(current_customer_id)
#     else:
#         print("there is no customer signed in")
#     return current_customer_id, current_order
# use this line when applying
# cuurent_customer_id, current_order = get_customer_id(answer)
###############################################################################################################
 
# creating the database and defining the connection and cursor

# creating all the classes
class Customer:
    "a class to store customers"
    def __init__(self,name, email, phone,customer_id = None):
        self.customer_id = customer_id 
        self.name = name
        self.email = email
        self.phone = phone
        
    
    def __repr__(self):
        return f'The customers name is {self.name} and email {self.email}'
    
    def save_to_db(self,connection,cursor):
      """A function to add a new customer into the db"""
      query = """
            INSERT INTO customers (name, email, phone)
            VALUES (:name, :email, :phone);
        """
      val = {'name':self.name,'email': self.email,'phone':self.phone}
      with connection:
        try:
          cursor.execute(query, val)          
          self.customer_id = cursor.lastrowid   # return the newest__id created 
          print(f'customer {self.name} saved into the db ')    
        except Exception as err:
          print('ERROR BY INSERT:', err)
         
    def remove(self,connection,cursor):
      """A function to remove customers"""
      with connection:
        try:
          cursor.execute("DELETE FROM customers")
          print(f'The customer{self.name} was removed from the table')
        except Exception as err:
          print('ERROR BY DELETE:', err)
      
class Product:
    "a class to store products"
    def __init__(self, name, price, quantity_in_stock,product_id = None):
        self.product_id = product_id 
        self.name = name
        self.price = price
        self.quantity_in_stock = quantity_in_stock
    
    def __repr__(self):
        return f'The products name is {self.name} and price is  {self.price}, there are {self.quantity_in_stock} in stock'
    
    def save_to_db(self,connection,cursor):
      """A function to add a new product into the db"""
      query = """
            INSERT INTO products (name, price, quantity_in_stock)
            VALUES (:name, :price, :quantity_in_stock);
        """
      val = {'name' :self.name, 'price':self.price, 'quantity_in_stock':self.quantity_in_stock}
      with connection:
        try:
          cursor.execute(query, val)
          self.product_id = cursor.lastrowid
          
          print(f'new product {self.name} was entered into the db')
        except Exception as err:
          print('ERROR BY INSERT product:', err)
          query2 = """ SELECT product_id FROM products WHERE name = :name"""
          val2 = {'name':self.name}
          cursor.execute(query2,val2)
          self.product_id = cursor.fetchall()[0][0]
          print(f'{self.product_id} for {self.name} saved')

     
    def remove(self,connection,cursor):
      """A funtion to remove a product from the db"""
      with connection:
        cursor.execute("DELETE from products")
        print(f'The customer{self.name} was removed from the table')

    def decrease_quantity(self,x,connection,cursor):
        # need to write a query to minus x from the inventory when something is bought.  
        #use Update query 
        query = "UPDATE products SET quantity_in_stock = quantity_in_stock - :x WHERE name = :name;"
        val = {'x':x,'name':self.name}
        with connection:
          cursor.execute(query,val)
          print(f'Quantity of {self.name} decreased by {x}')


class Order:

  def __init__(self, customer_id, date_time = None ,order_id = None):
    self.customer_id = customer_id
    self.date_time = date_time
    self.order_id = order_id 
  
  def __repr__(self):
    return f"This order occured at {self.date_time}"

  def save_to_db(self,connection,cursor):
    query = """
            
            INSERT INTO orders (customer_id)
            VALUES (:customer_id);
        """
    val= {'customer_id':self.customer_id}
    with connection:
      try:
        cursor.execute(query, val)
        self.order_id = cursor.lastrowid
        print(f'new order {self.order_id}  was entered into the db')
      except Exception as err:
        print('ERROR BY INSERT order:', err)

class Order_Item:

  def __init__(self,order_id,product_id,quantity,item_id = None):
    self.order_id = order_id
    self.product_id = product_id
    self.quantity = quantity
  
  def __repr__(self):
    return f'This order is for product {self.product_id},for {self.quantity} product.'
  
  def save_to_db(self,connection,cursor):
      """A function to add a new order_item into the db"""
      query = """
            INSERT INTO order_item (order_id, product_id, quantity)
            VALUES (:order_id, :product_id, :quantity);
        """
      val = {'order_id' :self.order_id, 'product_id':self.product_id, 'quantity':self.quantity}
      with connection:
        try:
          cursor.execute(query, val)
          self.item_id = cursor.lastrowid
          print(f'order_item {self.item_id} entered into the db')   
        except Exception as err:
          print('ERROR BY INSERT order_item:', err)
 
      
######################################################################################################3

def sql_query(query,connection):
  
  return pd.read_sql_query(query,connection)
     