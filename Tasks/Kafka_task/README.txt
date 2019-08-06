Exercise:

The system below uses Apache Kafka, we would like to validate one of its modules.
Please create a test module in C# that validates the “Processing” module (found in the flow below).

Messages processed consist of 3 values: id, name and a score (1.00 - 10.00).
“Processing” module consume new messages from “INPUT” Kafka topic.
“Processing” module multiply the input value of the score by 2 and produce a message to “OUTPUT” Kafka topic.

Test module should simulate incoming data by sending messages to the “INPUT” Kafka topic (appear as “Pub Sub” before
“Processing” module) and consume message from “OUTPUT” Kafka topic.

*Code does not need to compile but should use real Kafka syntax as much as possible.
========================================================================================================================

Requirements (for Linux mostly, for Windows differs path and script extensions):
1) Download kafka and move it to /usr/local/kafka
2) Start a ZooKeeper server on your system:
   ### /usr/local/kafka/bin/zookeeper-server-start.sh /usr/local/kafka/config/zookeeper.properties
3) Start the Kafka server:
   ### /usr/local/kafka/bin/kafka-server-start.sh /usr/local/kafka/config/server.properties
4) Install kafka-python
   ### pip install kafka-python
========================================================================================================================

Script run:
1) Script can be executed from shell on a host that have python3 (3.6+ version i assume) after all requirements are met:
    python3 kafka_test.py
========================================================================================================================

Notes:
This exercise could be achieved in few more ways:
1) in the same script run synchronously Producer that will send messages, than run Consumer that will receive them, than
run validation to test result. (1 process that was implemented for this exercise for easier execution like POC)
2) run Consumer as a separate process that will always listen and write all messages to a log file, than each Producer
run will send some messages and also will validate success. (2 processes)
3) run Consumer and Producer as a separate processes. Producer could take data from a file with messages, Consumer will
write all output messages to a new file, than compare two files with test script. It will help to test data at any moment
of time on already running services. (3 processes)
========================================================================================================================

Used info:
# https://kafka.apache.org/documentation/
# https://kafka-python.readthedocs.io/en/master/usage.html
# https://github.com/dpkp/kafka-python/blob/master/README.rst
# https://github.com/robinhood/faust  -- faust can be used to modify kafka's stream
