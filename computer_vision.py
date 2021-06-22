# use this to store all the computer vision functions
######################################################################################################3
import cv2

import numpy as np

def model_net(MODEL,WEIGHT):

  net = cv2.dnn.readNetFromDarknet(MODEL, WEIGHT)
  net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
  return net 

#net = model_net()    # this should only happen in the main part..? 


def forwardpassoutput(image,net,IMG_WIDTH,IMG_HEIGHT):
    """This takes the image coming from the webcam and returns the boxes, confidences for each class and class_ids and indexes"""
       #blob is what we need for the input into the net
    blob = cv2.dnn.blobFromImage(image,1/255,(IMG_WIDTH,IMG_HEIGHT),(0,0,0),crop = False)
     
    # running the model on the image. 
    net.setInput(blob)
    # getting the output layer this has the boxes probability of object and probabilities of each class
    output_layer_names = net.getUnconnectedOutLayersNames()
    layeroutput = net.forward(output_layer_names)

    frame_width = image.shape[0]
    frame_height = image.shape[1]

    boxes = []
    confidences = []
    class_ids = []
    # drawing the bounding boxes
    for output in layeroutput:
        for detection in output:
            score  = detection[5:]            
            class_id = np.argmax(score)
            confidence = score[class_id]
            if confidence > 0.7:
                center_x = int(detection[0]*frame_width)
                center_y = int(detection[1]*frame_height) 
                w = int(detection[2]*frame_width)        
                h = int(detection[3]*frame_height)

                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x,y,w,h])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    #non_max_suppression
    indexes = cv2.dnn.NMSBoxes(boxes, confidences,0.5, 0.4)

    return boxes , confidences, class_ids, indexes  # using the indexes 

def draw_boxes(result,boxes,confidences, class_ids,indexes,classes_name,colors,font):    
    label_keeper = []    
    for i in indexes.flatten():    # this used to have indexes.flatten()
        x,y,w,h,= boxes[i]
        label = str(classes_name[class_ids[i]])

        confi = str(round(confidences[i],2))
        cv2.rectangle(result,(x,y),(x+w,y+h),colors,5)
        cv2.putText(result,(label+" "+confi),(x,y+20),font,1,(255,255,255))
        label_keeper.append(label)

    return result, label_keeper

def receipt_writer(label_keeper,items_prices):
    purchase_list = []
    total_bill = 0
    for item in label_keeper:

            next_item = item + " " +  str(items_prices[item])
            total_bill += items_prices[item]    # this is the amount
            purchase_list.append(next_item)
    return  purchase_list , total_bill
 