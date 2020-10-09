# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Worker side of the Web Queue Worker architecture

import boto3
from datetime import datetime


def main():
    global client
    client = boto3.client('sqs')
    
    request_queue_url = client.get_queue_url(QueueName='request_queue')['QueueUrl']
    response_queue_url = client.get_queue_url(QueueName='response_queue')['QueueUrl']
    print("Request queue URL: " + request_queue_url)
    print("Response queue URL: " + response_queue_url)
    print('')

    # Wait for request
    just_processed_messages = True
    while True:
        if just_processed_messages:
            just_processed_messages = False
            print("Waiting for messages...")
        
        messages = client.receive_message(
            QueueUrl=request_queue_url,
            MaxNumberOfMessages=10
        )
        if 'Messages' in messages:
            for message in messages['Messages']: # Get the messages in queue
                print("Msg received @ " + datetime.now().strftime("%H:%M:%S") +
                      ": " + message['Body'], end="\n\n")
                body = message['Body']

                # Process data
                total = 0.0
                for s in body.split(','):
                    total += float(s)
                average = total / len(body.split(','))
                
                # Make a response
                send_msg(response_queue_url, str(average))
                
                # Delete the message from the queue as to not process it again
                client.delete_message(
                    QueueUrl=request_queue_url,
                    ReceiptHandle=message['ReceiptHandle']
                )
            just_processed_messages = True
            


def send_msg(queue_url, msg):
    sqs_response = client.send_message(
        QueueUrl=queue_url,
        MessageBody=msg
    )



if __name__ == "__main__":
    main()
