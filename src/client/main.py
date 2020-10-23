# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Client side of the Web Queue Worker architecture

import boto3
import time
from datetime import datetime
from guietta import Gui, _, III, ___, HSeparator, VSeparator
from PySide2.QtGui import QPixmap


def main():
    sqs = boto3.resource('sqs')
    s3 = boto3.resource('s3')
    
    # Get the queue urls
    request_queue = sqs.get_queue_by_name(QueueName='request_queue')
    response_queue = sqs.get_queue_by_name(QueueName='response_queue')
    bucket = s3.Bucket('julgio-cli-bucket')
    
    print('AWS connection done. Starting application...')

    curr_img = 1

    gui = Gui([ "Enter numbers:", _             , _         , _           , _ ],
              [ "__n1__"        , "__n2__"      , _         , _           , _ ],
              [ "__n3__"        , "__n4__"      , _         , _           , _ ],
              [ "__n5__"        , "__n6__"      , _         , _           , _ ],
              [ "__n7__"        , "__n8__"      , _         , _           , _ ],
              [ ["Go"]          , ___           , _         , _           , _ ],
              [ "Average: "     , "response"    , _         , _           , _ ],
              [ HSeparator      , ___           , ___       , ___         , ___ ],
              [ ("img1.jpg", "img"), ___        , VSeparator, ("img1.jpg", "img2"), ___ ],
              [ (["<"], "prev") ,([">"], "next"), III       , ["Effect 1"], ["Effect 2"] ])
    
    
    gui.title("Julien's Cloud Computing Lab3")
    gui.window().resize(500, 100)
    gui.response = "."

    # Handle ui events
    while True:
        name, event = gui.get()
        
        if name == None:
            # The user pressed the X (quits the app)
            break
        if name == 'Go':  # Calcuate the result
            # Fetch the values from the interface
            # The message must be comma seperated values
            message = str(gui.n1) + "," + str(gui.n2) + "," + str(gui.n3) + "," +\
                      str(gui.n4) + "," + str(gui.n5) + "," + str(gui.n6) + "," +\
                      str(gui.n7) + "," + str(gui.n8)

            send_average_request(request_queue, message)
            
            gui.response = "Waiting for response..."
            gui.widgets["Go"].setEnabled(False)  # Disable the go button while waiting for a response from worker
            gui.execute_in_background(  # Execute the queue monitoring funciton in a background thread as to not block the UI thread
                wait_for_response,
                args=[response_queue],
                callback=on_response_received
            )
        if name == "prev":  # Image precedente
            curr_img -= 1
            if curr_img == 0:
                curr_img = 4
            gui.widgets["img"].setPixmap(QPixmap("./img" + str(curr_img) + ".jpg"))
        if name == "next":  # Image suivante
            curr_img += 1
            if curr_img == 5:
                curr_img = 1
            gui.widgets["img"].setPixmap(QPixmap("./img" + str(curr_img) + ".jpg"))

def send_average_request(queue, msg):
    sqs_response = queue.send_message(
        MessageBody=msg,
        MessageAttributes={
            "RequestType" : {
                "StringValue" : "Average",
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
            #print("Response @ " + datetime.now().strftime("%H:%M:%S") + ": " + message.body)
            output = message.body
            message.delete()
            break
        
    return output


def on_response_received(gui, response_value):
    gui.response = response_value
    gui.widgets["Go"].setEnabled(True)  # The worker is done, give the hand back to the user


if __name__ == "__main__":
    main()
    
