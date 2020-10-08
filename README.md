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


*Julien Giovinazzo*