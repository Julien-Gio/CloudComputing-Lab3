# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Client side of the Web Queue Worker architecture

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
    
    while True:
        values = input("Values (comma seperated): ")
        send_msg(request_queue_url, values)
        wait_for_response(response_queue_url)


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
                  ": " +message['Body'])

            client.delete_message(
                QueueUrl=queue_url,
                ReceiptHandle=message['ReceiptHandle']
            )
            break

if __name__ == "__main__":
    main()
    
