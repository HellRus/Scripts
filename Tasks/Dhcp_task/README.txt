Exercise:

Managed slaves pool. Implement a HTTP server that manages a pool of 10 slaves,
each slave is represented by it's IP (192.168.0.101-192.168.0.110).

The server should listen to HTTP-GET requests at /get_slaves with the queries of `amount` and `duration`
In response the server should return the desired amount of slaves-IPs in json format if there are enough available,
otherwise it should return the wait time needed for enough slaves to get back to the pool (in seconds).

After returning the IPs, the server should remove those slaves from the pool until the end of the `duration`.

The server should run with a listening port number as argument.

example:
00:00:00 GET http://localhost:8080/get_slaves?amount=2&duration=10 -> get 2 IPs and removes them for 10 s from the pull
00:00:01 GET http://localhost:8080/get_slaves?amount=3&duration=13 -> get 3 IPs and removes them for 13 s from the pull
00:00:02 GET http://localhost:8080/get_slaves?amount=5&duration=15 -> get 5 IPs and removes them for 15 s from the pull
00:00:03 GET http://localhost:8080/get_slaves?amount=2&duration=10 -> returns not enough slaves, ask again in 7 s
00:00:11 GET http://localhost:8080/get_slaves?amount=2&duration=10 -> get 2 IPs and removes them for 10 s from the pull

json example:
{"slaves": ["192.168.0.101", "192.168.0.105"]}
{"slaves": [], "come_back": 7}

The server is expected to handle any edge-cases appropriately.
The server would be implemented with python 3x.

========================================================================================================================

How to run script from Linux environment:

### without additional argument as port, server will run and listen default 8080 port:
    $ python3 slaves_pool.py
### with additional argument as port:
    $ python3 slaves_pool.py 9090

### can be stopped by Ctrl+C (keyboard interrupt)


How to interact with server:

    $ curl 'http://localhost:9090/get_slaves?amount=2&duration=10'

In particular 'curl' request can be changed parameters: PORT, AMOUNT, DURATION
    PORT must be an integer in range from 1 to 65635
    AMOUNT must be an integer from 0 to 10 (can be exceeded to more by adjusting pool in the code
    DURATION must be an integer that stays for seconds