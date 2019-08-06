#! /usr/bin/env python3
import sys
import random
import copy
from time import sleep
from json import dumps, loads

try:
    from kafka import KafkaProducer, KafkaConsumer
except ImportError as error:
    sys.exit("'{}'. Please install the module 'kafka-python' and run the script again.".format(error))

__author__ = 'Anton Krylov'


class Producer(object):
    """
    This class is used to start or stop a kafka PRODUCER, it can be imported and used outside of this module
    """

    def __init__(self):
        self.bootstrap_servers = ['localhost:9092']
        self.value_serializer = lambda x: dumps(x).encode('utf-8')
        self.publisher = None

    def run(self):
        self.publisher = KafkaProducer(bootstrap_servers=self.bootstrap_servers, value_serializer=self.value_serializer)

    def stop(self):
        self.publisher.close()


class Consumer(object):
    """
    This class is used to start or stop a kafka CONSUMER, it can be imported and used outside of this module.
    Consumer have timeout for 5 sec for this test script, however a best practice will be to run the Consumer
    in the different process call and close by the stop method whenever it should be.
    """

    def __init__(self):
        self.bootstrap_servers = ['localhost:9092']
        self.value_serializer = lambda x: loads(x.decode('utf-8'))
        self.client = None

    def run(self):
        self.client = KafkaConsumer('tester',
                                    bootstrap_servers=self.bootstrap_servers,
                                    auto_offset_reset='earliest',
                                    group_id='my-group',
                                    value_deserializer=self.value_serializer,
                                    consumer_timeout_ms=5000
                                    )

    def stop(self):
        self.client.close()


events_amount = 5  # How many messages will be generated in the test
producer = Producer()
consumer = Consumer()
original_data = []
consumer_messages = []


def build_data():
    """
    This function is used to generate quantity of messages, provided in the global variable 'events_amount'.
    It's fast way to use this generator for test POC instead of manual value typing via script arguments
    """
    for e in range(events_amount):
        data = {
            "id": e,  # an integer from 0 to value provided in parameter 'events_amount'
            "name": "Message" + str(e),  # a string "Message" + integer from "id"
            "score": round(random.uniform(0.01, 10), 2)  # a random float 0.00-10.00
        }
        original_data.append(data)


def produce():
    """
    Function is strictly used to multiply 'score' by 2 and send to the Consumer.
    To simulate 'processing' module from the given task and prevent changes in the 'original_data' dictionary
    it copied as a new object and all interactions will be performed on it.
    """
    for element in copy.deepcopy(original_data):
        element["score"] *= 2
        producer.publisher.send('tester', value=element)
        sleep(1)  # may be omitted, but added just for more output readability


def consume():
    # get modified values from consumer and store them into new list
    for element in consumer.client:
        element = element.value
        consumer_messages.append(element)
        print("{} message added to the consumer".format(element))


def validate_success():
    """
    This function iterates through two data arrays and compares value in the 'score' fields:
    First list with original data that was sent to the Producer
    Second list with modified (multiplied by 2) data from the Consumer
    """
    for original in original_data:
        id_orig = original['id']
        score_orig = original['score']
        for modified in consumer_messages:
            id_mod = modified['id']
            score_mod = modified['score']
            if id_orig == id_mod:
                if score_orig * 2 == score_mod:
                    print("Messages with id '{}' have scores '{}' and '{}' and passed SUCCESS validation".format(
                        id_orig, score_orig, score_mod))
                else:
                    print("FAILED for id '{}' have not expected scores: '{}' and '{}'"
                          .format(id_orig, score_orig, score_mod))

    print("\nORIGINAL DATA passed to the producer:\n'{}'".format(original_data))
    print("\nMODIFIED DATA received from the consumer:\n'{}'".format(consumer_messages))


def test_run():
    # Test stream that will prepare messages, send them via produce, get messages from consumer and validate success
    build_data()
    produce()
    consume()
    validate_success()


def main():
    producer.run()
    consumer.run()
    test_run()
    producer.stop()
    consumer.stop()  # Must be used if Consumer running as a separate process


if __name__ == '__main__':
    main()
