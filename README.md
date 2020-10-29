# CloudComputing-Lab3
 Work for lab3 of the AWS Cloud Computing course

# Amazon SQS
Amazon's Simple Queue Service is a message queuing service that can easly scale. You can send, store and receive data between machines without complexity or overhead.
There are two types of message queues in SQS
*Standard queues* are built for maximum throughput. They garantee at-least-once delivery of messages.
*FIFO queues* aim to provide messages exactly once, in the same order that they are sent.

# Web Queue Worker architecture
The Web Queue Worker architecture has two main parts to it. A **web front end** and a **worker**. The web front end handles client HTTP requests, while the worker takes care of processing tasks (intensive computations, long tasks, batch jobs, etc). These two parts communicate using a **message queue**.
This architecture is very light and easy to deploy. The principle of seperation of concerns is respected; the front end is desyncronised and independent from the worker. This allows one to scale the front end and worker separately.
This architechture is great for simple applications or applications with batch operations / long-running jobs.


# My work
## Setting up the worker in AWS CLI
Since the worker script has to run on a server, we will be using an AWS EC2 instance to handle this.
The first step is to launch (create) the EC2 instance. We will use a pre-made key and security group :
```bash
aws ec2 run-instances --image-id "ami-0947d2ba12ee1ff75" --count 1 --instance-type t2.micro --key-name myKey --security-group-ids "sg-07ed9af48bea7190e"
```
Then we need to get all the necesary libraries for the worker to run. Here are all the python libraries we need (and what for):
* ```boto3``` : to easly interact with the AWS API.
* ```wheel``` : needed to install scikit-image.
* ```scikit-image```: for image processing (includes many other libraries like ```numpy``` by default).

But we will also need the following:
* ```python3``` : to run python scripts. Also comes with ```pip3```.
* ```g++``` : necessary for ```scikit-image```.
* ```python3-devel``` : necessary for ```scikit-image```.

Here are the commands:
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
With our instance ready to go, we must now start it and launch the worker script. This requires many intermediate steps.
Here are the different steps in my worker_init bash script.

### 1) Passing the lastest version of the script and credentials
Obviously the instance must receive the python code to be able to run it. Also, for the script to be able to comminicate with the SQS and S3 buckets, it needs the latest AWS credentials.
For now we store these files as strings in two variables. We will then paste them in our instance at a later point (step 3):
```bash
credentials=$( cat "[path to credentials]" )
code=$( cat "[path to worker script]" )
```

### 2) Starting the instance
Now me can start our instance. The boot time is variable but usually takes about 30 seconds. By waiting 45 seconds, we make sure that we can connect.
We must also get the instance's public ip address to establish an SSH connection later.
```bash
aws ec2 start-instances --instance-ids "[instance id]"
sleep 45
ip=$( aws ec2 describe-instances --instance-ids "i-068d57622c916ab92" --query "Reservations[*].Instances[*].PublicIpAddress" --output text )
```

### 3) Send commands to instance
To send commands to the instance we will be using a Secure Shell connection. To establish a communcaiton, we need two things.
First, we need ths instance's public DNS. You can see it's strucutre on the first line. (Note, the ip address looks like this "192.168.0.1", we use ```${ip//./-}``` to make it like so "192-168-0-1").
Finaly, we need the associated key.
Then we pass it the commands to update the credentials, the worker code, and execute it.
```bash
myarg="ec2-user@ec2-${ip//./-}.compute-1.amazonaws.com"

cd "[path to folder with myKey.pem]"
ssh -i "myKey.pem" $myarg << EOF

# Instance commands
echo "$credentials" > ~/.aws/credentials
echo "$code" > ~/lab3/main.py
python3 ~/lab3/main.py

# En of connection
EOF
```

# The Client
TODO

# The Worker
TODO


*Julien Giovinazzo*
