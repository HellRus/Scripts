#! /usr/bin/env python3
import sys
import re
import time
import json
from datetime import datetime, timedelta

try:
    import urllib.request
    import urllib.parse
    from http.server import BaseHTTPRequestHandler, HTTPServer
except ImportError as error:
    sys.exit("'{}'. Please install the module 'kafka-python' and run the script again.".format(error))

__author__ = 'Anton Krylov'

PORT = 8080  # default port, can be replaced with custom
HOSTNAME = "localhost"


class MyServer(BaseHTTPRequestHandler):
    ips = ["192.168.0." + str(x) for x in range(101, 111)]  # Create dict with IPs, can be grown by interact with range
    slaves = dict.fromkeys(ips, 0)

    def do_GET(self):
        # This method will handle all get request with additional validation by values, types and path.
        self.send_response(200)
        self.send_header('content-type', 'text/html')
        self.end_headers()
        timestamp = datetime.now()
        if re.search("/get_slaves*", self.path):
            query_components = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
            try:
                amount = int(query_components["amount"][0])
                duration = int(query_components["duration"][0])
                json_response = self.get_slaves(amount, duration, timestamp)
                if json_response is not None:
                    self.wfile.write(json_response.encode())
            except:
                self.wfile.write("ERROR: request may contain incorrect 'amount' and 'duration' values. Must be only "
                                 "numbers and 'amount' must be less or equal to available IPs in the pool".encode())
        else:
            self.wfile.write("ERROR: url request is malformed".encode())

    def get_slaves(self, amount, duration, timestamp):
        """
        Method is used to check if there is enough IPs in pool, assign time to lease to IPs and return response
        in JSON format.
        :param amount: integer, that describes how many IPs requested by user
        :param duration: integer, time in seconds for 'lease' IPs
        :param timestamp: object that stored automatically in do_GET function.
        :return: json response to end user (by do_GET function)
        """
        time_to_wait = self.free_slaves(timestamp)
        available_now = self.available_slaves()
        ready = []
        wait_till = timestamp + timedelta(seconds=duration)
        if amount <= len(available_now):
            for i in available_now[:amount]:
                ready.append(i)  # update with current timestamp + duration (lease time)
                self.slaves[i] = wait_till
            json_response = json.dumps({"slaves": ready})
            return json_response
        else:
            needs = amount - len(available_now)  # calculate how many IPs we must wait
            wait = sorted(time_to_wait)[needs - 1]  # get end of lease time of the last needed IP
            json_wait = json.dumps({"slaves": ready, "come_back": wait})
            return json_wait

    def free_slaves(self, timestamp):
        """
        This method is used to flush all IPs with exceeded lease time and store info 'end of lease time' in seconds
        :param timestamp: object that stored automatically in do_GET function.
        :return: list of integers, that are seconds wait till end of lease for each busy IP
        """
        time_to_wait = []
        for key, value in self.slaves.items():
            if value is not 0:
                diff = (value - timestamp).total_seconds()  # how many seconds wait to end of lease
                if diff < 0:
                    self.slaves[key] = 0  # release IP address with 0 value instead of timestamp
                elif diff > 0:
                    time_to_wait.append(int(diff))
        # THIS block can be uncommented to help debug assign between IP and lease time
        # output = ""
        # for k, v in self.slaves.items():
        #     if v is not 0:
        #         output += "{0} - {1} | ".format(k.split('.')[-1], v.strftime("%H:%M:%S"))
        #     else:
        #         output += "{0} - 0 | ".format(k.split('.')[-1])
        # print(output)
        return time_to_wait

    def available_slaves(self):
        """
        This method helps to get all currently available to lease IPs.
        :return: list of IPs
        """
        available = []
        for key, value in self.slaves.items():
            if value == 0:
                available.append(key)
        return available


def main():
    global PORT
    if len(sys.argv) > 0:
        try:
            PORT = int(sys.argv[1])
        except:
            print("Can't read port value, using default")
            pass
    # Create a web server and define the handler to manage the incoming request
    pool_server = HTTPServer((HOSTNAME, PORT), MyServer)
    print(time.asctime(), "Server Starts - '{}':'{}'".format(HOSTNAME, PORT))
    try:
        pool_server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down the web server')
        pool_server.socket.close()
        pool_server.server_close()
        print(time.asctime(), "Server Stops - '{}':'{}'".format(HOSTNAME, PORT))


if __name__ == '__main__':
    main()
