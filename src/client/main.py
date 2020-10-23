# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Client side of the Web Queue Worker architecture

import boto3
import time
from datetime import datetime
from guietta import Gui, _, III, ___, HSeparator, VSeparator
from PySide2.QtGui import QPixmap


def main():
    global bucket
    sqs = boto3.resource('sqs')
    s3 = boto3.resource('s3')
    
    # Get the queue urls
    request_queue = sqs.get_queue_by_name(QueueName='request_queue')
    response_queue = sqs.get_queue_by_name(QueueName='response_queue')
    bucket = s3.Bucket('julgio-cli-bucket')
    
    print('AWS connection done. Starting application...')

    curr_img = 1

    gui = Gui([ "Enter numbers:"   , _             , _         , _    , _ ],
              [ "__n1__"           , "__n2__"      , _         , _    , _ ],
              [ "__n3__"           , "__n4__"      , _         , _    , _ ],
              [ "__n5__"           , "__n6__"      , _         , _    , _ ],
              [ "__n7__"           , "__n8__"      , _         , _    , _ ],
              [ ["Go"]             , ___           , _         , _    , _ ],
              [ "Average: "        , "response"    , _         , _    , ___ ],
              [ HSeparator         , ___           , ___       , ___  , ___ ],
              [ ("img1.jpg", "img"), ___           , VSeparator, ("img1.jpg", "img2"), ___ ],
              [ (["<"], "prev")    ,([">"], "next"), III       , ["Effect 1"], ["Effect 2"] ])
    
    
    gui.title("Julien's Cloud Computing Lab3")
    gui.window().resize(500, 100)
    gui.response = "."
    gui.img_label = ""

    # Handle ui events (e.g. button presses)
    while True:
        name, event = gui.get()
        
        if name == None:
            # The user pressed the X (quits the app)
            break
        
        elif name == 'Go':  # Calcuate the result
            # Fetch the values from the interface
            # The message must be comma seperated values
            message = str(gui.n1) + "," + str(gui.n2) + "," + str(gui.n3) + "," +\
                      str(gui.n4) + "," + str(gui.n5) + "," + str(gui.n6) + "," +\
                      str(gui.n7) + "," + str(gui.n8)

            send_average_request(request_queue, message)
            
            gui.response = "Waiting for response..."
            gui.widgets["Go"].setEnabled(False)  # Disable the go button while waiting for a response from worker

            # Execute the queue monitoring funciton in a background thread as to not block the UI thread
            gui.execute_in_background(
                wait_for_response,
                args=[response_queue],
                callback=on_response_received
            )
            
        elif name == "prev":  # Image precedente
            curr_img -= 1
            if curr_img == 0:
                curr_img = 4
            gui.widgets["img"].setPixmap(QPixmap("./img" + str(curr_img) + ".jpg"))
            
        elif name == "next":  # Image suivante
            curr_img += 1
            if curr_img == 5:
                curr_img = 1
            gui.widgets["img"].setPixmap(QPixmap("./img" + str(curr_img) + ".jpg"))

        elif name.startswith("Effect"):
            ### Apply effect to selected image
            # Step 1 : Upload image to s3 bucket
            # Step 2 : Display "loading" image
            # Step 3 : Send message with the image link and effect number
            # Step 4 : Wait for response
            ###
            
            # Step 1
            img_destination = "lab3_img.jpg"
            bucket.upload_file("img" + str(curr_img) + ".jpg", img_destination)
            
            # Step 2
            gui.widgets["img2"].setPixmap(QPixmap("./imgLoad.jpg"))
            gui.widgets["Effect1"].setEnabled(False)  # Also disable buttons
            gui.widgets["Effect2"].setEnabled(False)

            # Step 3
            # The message is "[image path in bucket],[Effect number]"
            message = img_destination + ","
            if name == "Effect1":
                message += "1"
            elif name == "Effect2":
                message += "2"
            send_image_request(request_queue, message)
                
            # Step 4
            # Execute the queue monitoring funciton in a background thread as to not block the UI thread
            gui.execute_in_background(  
                wait_for_response,
                args=[response_queue],
                callback=on_response_received
            )


def send_average_request(queue, msg):
    queue.send_message(
        MessageBody=msg,
        MessageAttributes={
            "RequestType" : {
                "StringValue" : "Average",
                "DataType" : "String"
            }
        }
    )


def send_image_request(queue, msg):
    queue.send_message(
        MessageBody=msg,
        MessageAttributes={
            "RequestType" : {
                "StringValue" : "ImageEffect",
                "DataType" : "String"
            }
        }
    )


def wait_for_response(queue):
    print("Waiting for response...")
    output = "?"
    while output == "?":
        time.sleep(1)  # Dont fetch too often, or else I'm going to run out of AWS credits
        messages = queue.receive_messages(
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All']
        )
        for message in messages:
            response_type = message.message_attributes["ResponseType"]["StringValue"]
            #print("Response @ " + datetime.now().strftime("%H:%M:%S") + ": " + message.body)
            output = message.body
            message.delete()
            break
        
    return output, response_type


def on_response_received(gui, response_value, response_type):
    if response_type == "Average":
        gui.response = response_value
        gui.widgets["Go"].setEnabled(True)  # The worker is done, give the hand back to the user

    elif response_type == "ImageEffect":
        # Fetch image from bucket
        bucket.download_file(response_value, "img_with_effect.jpg")
        # Display it
        gui.widgets["img2"].setPixmap(QPixmap("./img_with_effect.jpg"))
        gui.widgets["Effect1"].setEnabled(True)
        gui.widgets["Effect2"].setEnabled(True)
        

if __name__ == "__main__":
    main()
    
