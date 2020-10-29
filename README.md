# CloudComputing-Lab3
 Work for lab3 of the AWS Cloud Computing course

# Amazon SQS
Amazon's Simple Queue Service is a message queuing service that can easly scale. You can send, store and receive data between machines without complexity or overhead.
There are two types of message queues in SQS:
* **Standard queues** are built for maximum throughput. They garantee at-least-once delivery of messages.
* **FIFO queues** aim to provide messages exactly once, in the same order that they are sent.

Even though a FIFO queue would arguably be a better fit for this projec, I will be using a Standard Queue because of the limitation of my student AWS account.

# Web Queue Worker architecture
The Web Queue Worker architecture has two main parts to it. A **web front end** and a **worker**. The web front end handles client HTTP requests, while the worker takes care of processing tasks (intensive computations, long tasks, batch jobs, etc). These two parts communicate using a **message queue**.
This architecture is very light and easy to deploy. The principle of seperation of concerns is respected; the front end is desyncronised and independent from the worker. This allows one to scale the front end and worker separately.

This architechture is great for simple applications or applications with batch operations / long-running jobs.


# My work
## Setting up the worker in AWS CLI
Since the worker script has to run on a server, we will be using an AWS EC2 instance to handle this.

The first step is to launch (create) the EC2 instance. We will use a pre-made key and security group:
```bash
aws ec2 run-instances --image-id "ami-0947d2ba12ee1ff75" --count 1 --instance-type t2.micro --key-name myKey --security-group-ids "sg-07ed9af48bea7190e"
```

Then, we need to get all the necesary libraries for the worker to run our script. Here are all the python libraries we need:
* `boto3` : to easly interact with the AWS API.
* `wheel` : needed to install `scikit-image`.
* `scikit-image`: for image processing (includes many other libraries such as `numpy` by default).

But we will also need the following:
* `python3` : to run our python script. Also comes with `pip3`.
* `g++` : necessary for `scikit-image`.
* `python3-devel` : also necessary for `scikit-image`.

Here are the commands in the right order:
```
sudo yum update
sudo yum install python3 -y
sudo yum install gcc -y
sudo yum install gcc-c++ -y
sudo yum install python3-devel -y
sudo pip3 install boto3
sudo pip3 install wheel
sudo pip3 install scikit-image
```

## Launching the worker script
With our instance ready to go, we must now start it and execute the worker script. This requires many intermediate steps.
Here are the different steps in my bash script.

### Step 1) Passing the lastest version of the script and credentials
For the script to be able to comminicate with the SQS and S3 buckets, it needs the latest AWS credentials of my account.
For now we store this file as a string in a variable. We will then paste it in our instance at a later point (see step 3):
```bash
credentials=$( cat "[path to credentials]" )
```

### Step 2) Starting the instance
We can now start our instance. The boot time is variable but usually takes around 30 seconds. Hence, by waiting 45 seconds, we make sure that we can connect.
We must also retreive the instance's public ip address to establish an SSH connection in the next step.
```bash
aws ec2 start-instances --instance-ids "[instance id]"
sleep 45
ip=$( aws ec2 describe-instances --instance-ids "i-068d57622c916ab92" --query "Reservations[*].Instances[*].PublicIpAddress" --output text )
```

### Step 3) Send commands to the instance
To send commands to the instance we will be using a Secure Shell connection. To establish a communcaiton, we need two things.

First, we need the instance's public DNS. You can see it's strucutre on the first line of code below. (Note, the retreived ip address has the following format: "192.168.0.1", we use `${ip//./-}` to change it to this format: "192-168-0-1").

Finally, we need the associated SSH key.

Then we send the commands to update the credentials and of course execute the worker script.
```bash
myarg="ec2-user@ec2-${ip//./-}.compute-1.amazonaws.com"

cd "[path to folder with myKey.pem]"
ssh -i "myKey.pem" $myarg << EOF

# Instance commands
echo "$credentials" > ~/.aws/credentials
python3 ~/lab3/main.py

# End of connection
EOF
```

You can see the full script in `init_script.sh`. We are now ready to use our client software from anywhere.

# The UI
![img](https://github.com/Julien-Gio/CloudComputing-Lab3/blob/master/img/UI_ex1.png?raw=true)

# Features
## Calculating the average
In the top section of the UI, a user can fill in 8 values. By pressing "Go", a message is sent to the worker to calculate the median, mean, min, and max of those values. While waiting for the result, the interface simply displays "Waiting for response...": 

![img](https://github.com/Julien-Gio/CloudComputing-Lab3/blob/master/img/UI_average_sending.png?raw=true)

Then, once the worker is done, the appropriate values are displayed.

## Applying effects to images
Using the arrows in the bottom left of the UI, the user can choose an image of their liking. Then click on "Effect 1" or "Effect 2" to send a request to the worker.
Much like the average portion, a temprary image is dispayled while waiting for an answer from the worker.

![img](https://github.com/Julien-Gio/CloudComputing-Lab3/blob/master/img/UI_image_sending.png?raw=true)

Here are the two effects:
* Effect 1: desaturation / black & white
![img](https://github.com/Julien-Gio/CloudComputing-Lab3/blob/master/img/UI_effect1.png?raw=true)
* Effect 2: Horizontal flip
![img](https://github.com/Julien-Gio/CloudComputing-Lab3/blob/master/img/UI_effect2.png?raw=true)

## Other features
Another small feature that is present in the software is that the UI prevents the user from sending multiple messages in parallel. For example, while waiting for the worker to do calculations on the numerical values, the "Go" button will be disabled. It will be re-enabled once the worker has responded. This is because there is no guarente of order of the messages in the queue (we are using a Standard Queue).

The same priciple is applyed to the image effect part of the UI.

---

*October 29 2020 - Julien Giovinazzo*
