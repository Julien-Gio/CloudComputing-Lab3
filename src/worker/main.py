# Julien Giovinazzo - Oct 2020
# FISE3 Cloud Computing - lab3

# Worker side of the Web Queue Worker architecture

import boto3
import time
from datetime import datetime
from skimage.io import imread, imsave
from numpy import flipud, uint8, median, mean, ma



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
            print("Processing data...")
            body = message.body
            request_type = message.message_attributes["RequestType"]["StringValue"]

            # Process data
            if request_type == "Average":
                numbers = []
                for s in body.split(','):
                    numbers.append(float(s))
                mediane_val = median(numbers)
                mean_val = mean(numbers)
                min_val = ma.min(numbers)
                max_val = ma.max(numbers)
                
                # Make a response
                answer = str(median_val) + "," + str(mean_val) + "," + str(min_val) + "," + str(max_val)
                send_msg(response_queue, answer, "Average")
                log_data = "Msg received @ " + datetime.now().strftime("%H:%M:%S") + \
                           ": " + body + ". Response => " + answer + "\n"

            elif request_type == "ImageEffect":
                filename = body.split(',')[0]
                effect_num = body.split(',')[1]
                # Download image
                bucket.download_file(filename, "img_downloaded.jpg")

                # Apply effect
                if effect_num == "1":
                    # Black and white effect
                    bw_img = imread("img_downloaded.jpg", as_gray=True)
                    # bw_img = bw_img.astype(uint8) # Ne marche que sous W10 :/
                    imsave("img_downloaded.jpg", bw_img)
                elif effect_num == "2":
                    # Flip the image
                    flip_img = imread("img_downloaded.jpg")
                    flip_img = flipud(flip_img)
                    flip_img = flip_img.astype(uint8)
                    imsave("img_downloaded.jpg", flip_img)
                
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
