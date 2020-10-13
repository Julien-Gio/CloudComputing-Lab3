# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Client side of the Web Queue Worker architecture

import boto3
from datetime import datetime
from guietta import Gui, _, III


def main():
    global client, request_queue_url, response_queue_url
    client = boto3.client('sqs')

    # Get the queue urls
    request_queue_url = client.get_queue_url(QueueName='request_queue')['QueueUrl']
    response_queue_url = client.get_queue_url(QueueName='response_queue')['QueueUrl']
    print("Request queue URL: " + request_queue_url)
    print("Response queue URL: " + response_queue_url)
    print('')

    gui = Gui([ "Enter numbers:", "__n1__"  , "__n2__", "__n3__", "__n4__", ["Go"] ],
              [ III             , "__n5__"  , "__n6__", "__n7__", "__n8__", III    ],
              [ "Result: "      , "response", _       , _       , _       , _      ])
    
    gui.title("Julien's Cloud Computing Lab3")
    gui.window().resize(500, 100)
    gui.response = "."

    # Handle ui events
    while True:
        name, event = gui.get()
        print(name, event)
        if name == None:
            # The user pressed the X (quits the app)
            break
        if name == 'Go':  # Calcuate the result
            # The message must be comma seperated values
            message = str(gui.n1) + "," + str(gui.n2) + "," + str(gui.n3) + "," +\
                      str(gui.n4) + "," + str(gui.n5) + "," + str(gui.n6) + "," +\
                      str(gui.n7) + "," + str(gui.n8)
            send_msg(request_queue_url, message)

            gui.response = "Waiting for response..."
            gui.widgets["Go"].setEnabled(False)  # Disable the go button while waiting for a response from worker
            gui.execute_in_background(  # Execute the queue monitoring funciton in a background thread as to not block the UI thread
                wait_for_response,
                args=[response_queue_url],
                callback=on_response_received
            )
            
    

def send_msg(queue_url, msg):
    sqs_response = client.send_message(
        QueueUrl=queue_url,
        MessageBody=msg
    )


def wait_for_response(queue_url):
    print("Waiting for response...")
    
    while True:
        sqs_response = client.receive_message(
            QueueUrl=queue_url,
            MaxNumberOfMessages=1,
            MessageAttributeNames=['All']
        )
        
        if 'Messages' in sqs_response:
            message = sqs_response['Messages'][0]
            print("Response @ " + datetime.now().strftime("%H:%M:%S") +
                  ": " + message['Body'])

            client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            break

    return message['Body']


def on_response_received(gui, response_value):
    gui.response = response_value
    gui.widgets["Go"].setEnabled(True)  # The worker is done, give the hand back to the user


if __name__ == "__main__":
    main()
    
