# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Client side of the Web Queue Worker architecture

import boto3
import time
from datetime import datetime
from guietta import Gui, _, III


def main():
    sqs = boto3.resource('sqs')
    
    # Get the queue urls
    request_queue = sqs.get_queue_by_name(QueueName='request_queue')
    response_queue = sqs.get_queue_by_name(QueueName='response_queue')
    print('AWS connection done. Starting application...')

    gui = Gui([ "Enter numbers:", "__n1__"  , "__n2__", "__n3__", "__n4__", ["Go"] ],
              [ III             , "__n5__"  , "__n6__", "__n7__", "__n8__", III    ],
              [ "Result: "      , "response", _       , _       , _       , _      ])
    
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
    
