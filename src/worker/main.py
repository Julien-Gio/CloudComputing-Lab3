# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Worker side of the Web Queue Worker architecture

import boto3
import time
from datetime import datetime


def main():
    sqs = boto3.resource('sqs')
    s3 = boto3.resource('s3')

    request_queue = sqs.get_queue_by_name(QueueName='request_queue')
    response_queue = sqs.get_queue_by_name(QueueName='response_queue')
    bucket = s3.Bucket('julgio-cli-bucket')
        
    print("Julien's worker script. Calculates the average of any list of values sent")
    print("through Amazon SQS. (Press Ctrl+C to quit at any time)\n")

    # Wait for request
    just_processed_messages = True
    while True:
        if just_processed_messages:
            just_processed_messages = False
            print("Waiting for messages...")

        
        time.sleep(1)  # Dont fetch too often, or else I'm going to run out of AWS credits
        messages = request_queue.receive_messages(
            MessageAttributeNames=["RequestType"],
            MaxNumberOfMessages=1
        )
        for message in messages: # Get the messages in queue
            body = message.body
            request_type = message.message_attributes["RequestType"]["StringValue"]

            # Process data
            if request_type == "Average":
                total = 0.0
                for s in body.split(','):
                    total += float(s)
                average = total / len(body.split(','))

                # Make a response
                send_msg(response_queue, str(average), "Average")
                log_data = "Msg received @ " + datetime.now().strftime("%H:%M:%S") + \
                           ": " + body + ". Response => " + str(average) + "\n"

            elif request_type == "ImageEffect":
                filename = body.split(',')[0]
                effect_num = body.split(',')[1]
                # Download image
                bucket.download_file(filename, "img_downloaded.jpg")

                # Apply effect
                # TODO
                
                # Upload image
                bucket.upload_file("img_downloaded.jpg", filename)
                
                # Send response message
                send_msg(response_queue, filename, "ImageEffect")
                log_data = "Msg recieved @ " + datetime.now().strftime("%H:%M:%S") + \
                           ": " + body + ". Effect " + effect_num + " applied\n"
            else:
                # This is never supposed to happen
                print("/!\\ Error, request type unknown : '" + request_type + "'")
                log_data = ""
                
            # Get log file from S3
            bucket.download_file('log.txt', 'log_downloaded.txt')

            # Update log
            with open('log_downloaded.txt', 'a') as f:
                f.write(log_data)

            # Push log on S3 bucket
            bucket.upload_file('log_downloaded.txt', 'log.txt')


            # Delete the message from the queue as to not process it again
            message.delete()

            just_processed_messages = True
            


def send_msg(queue, msg, response_type):
    sqs_response = queue.send_message(
        MessageBody=msg,
        MessageAttributes={
            "ResponseType" : {
                "StringValue" : response_type,
                "DataType" : "String"
            }
        }
    )



if __name__ == "__main__":
    main()
