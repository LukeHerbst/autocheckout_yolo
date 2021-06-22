# use this to keep all the dictionaries 
import cv2
classes_num = {'chips':0, 'milk': 1, 'oreo': 2, 'snickers': 3,"sting": 4}  # should probably get the classes from the .name folder to make it robust
classes_name  = {classes_num[num]:num for num in classes_num}
items_prices = {'sting':12000,'oreo':15000,'milk':33000,'snickers':22000,'chips':30000}  # this should also be sourced from a seperate place maybe a db maybe a df ? 
                                                                                       
IMG_WIDTH, IMG_HEIGHT = 416, 416
font = cv2.FONT_HERSHEY_PLAIN
colors  = (0,255,0)                                                                    
MODEL = r'C:\Users\Luke\Desktop\final project\custom-yolov4-detector.cfg'

WEIGHT = r'C:\Users\Luke\Desktop\final project\custom-yolov4-new_best.weights'

query_dictionary = {'all_products':'SELECT * FROM products',
                    'last_10_customers':'SELECT * FROM customers LIMIT 10',
                    'recent_order_history': 
"""
SELECT c.name as customer_name ,o.date_time as time_of_order, SUM(p.price) as order_total  
FROM customers as c
JOIN orders as o
USING (customer_id)
JOIN order_item as ot
USING (order_id)
JOIN products as p 
USING (product_id)
GROUP BY c.name
ORDER BY o.date_time
""",
'most_popular_products':
"""
SELECT p.name, SUM(ot.quantity) as total 
FROM products as p
JOIN order_item as ot
USING (product_id)

GROUP BY p.name
ORDER BY total DESC  
""",
'best_customers':"""
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
'all_orders': 'SELECT * FROM orders LIMIT 10'
}