# use this to keep all the dictionaries 
import cv2
import numpy as np

def get_class_names(path):
  with open(path) as f:
    lines = f.readlines()
    test_dict = {i.strip('\n'):lines.index(i) for i in lines}
    return test_dict

path = r'C:\Users\Luke\Desktop\final project\obj.names'


classes_num = get_class_names(path)
classes_name  = {classes_num[num]:num for num in classes_num}
items_prices = {'sting':12000,'oreo':15000,'milk':33000,'snickers':22000,'chips':30000,'crackers':18000,'kitkat' : 20000,'pepsi':12000}  # this should also be sourced from a seperate place maybe a db maybe a df ? 


IMG_WIDTH, IMG_HEIGHT = 416, 416
font = cv2.FONT_HERSHEY_PLAIN
colors = (0,255,0)
# colors  = np.random.uniform(0,255,3)                                                      
MODEL = r'C:\Users\Luke\Desktop\final project\custom-yolov4-tiny-detector.cfg'

WEIGHT = r'C:\Users\Luke\Desktop\final project\custom-yolov4-tiny-detector_best.weights'

query_dictionary = {'Inventory':'SELECT * FROM products',
                    'Newest Customers':'SELECT * FROM customers ORDER BY customer_id DESC LIMIT 10 ',
                    'Recent Order History': 
"""
SELECT c.name as customer_name , SUM(p.price) as order_total  , o.date_time as time_of_order
FROM customers as c
JOIN orders as o
USING (customer_id)
JOIN order_item as ot
USING (order_id)
JOIN products as p 
USING (product_id)
GROUP BY o.order_id
ORDER BY o.date_time DESC
""",
'Most Popular Products':
"""
SELECT p.name as Product , SUM(ot.quantity) as Total_sold
FROM products as p
JOIN order_item as ot
USING (product_id)
GROUP BY p.name
ORDER BY Total_sold DESC  
""",
'Best Customers':"""
SELECT c.name as customer_name , SUM(p.price) as total_spent  
FROM customers as c
JOIN orders as o
USING (customer_id)
JOIN order_item as ot
USING (order_id)
JOIN products as p 
USING (product_id)
GROUP BY c.name
ORDER BY total_spent DESC
""",

}