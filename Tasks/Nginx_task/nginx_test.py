import sys
import os
import logging
import random
import subprocess

try:
    import requests
    import string
except ImportError as error:
    sys.exit("'{}'. Please install the module and run the script again.".format(error))

__author__ = 'Anton Krylov'


class NginxTest(object):
    _http_headers = {
        "User-Agent": ('Chrome', 'Safari'),
        "HTTP Version": ('HTTP/1.1', 'HTTP/1.0')
    }

    log_name = "report.data"
    log_path = ""
    log = os.path.join(log_path, log_name)
    logging.basicConfig(filename=log, level=logging.INFO, format="[%(asctime)s]:[%(levelname)s]:%(message)s")

    def __init__(self):
        self.nginx_ip = "http://127.0.0.1"
        self.container_name = "nginxTest"
        self.success_http_code = 200

    @staticmethod
    def check_docker_status():
        """
        Method is used to verify that Docker is running on local machine
        """
        terminal_command = "service docker status"
        success_code = "Active: active (running)"
        output_line = subprocess.getstatusoutput(terminal_command)
        output_line = output_line[1].split("\n")

        for line in output_line:
            if success_code in line:
                logging.info("Docker is active and running.")
                return  # exception
        logging.error("Docker is inactive.")

    def check_previous_nginx_instance(self):
        """
        This method is used to remove previous nginx instance to create a new one after
        """
        logging.info("Checking for previous installed nginx container named '{}'".format(self.container_name))
        terminal_stop_command = "docker stop '{}'".format(self.container_name)
        terminal_remove_command = "docker rm '{}'".format(self.container_name)
        if self.nginx_validate():
            output_stop_line = subprocess.getoutput(terminal_stop_command)
            output_remove_line = subprocess.getoutput(terminal_remove_command)
            logging.info("Nginx container with name '{}' was removed successfully".format(self.container_name))

    def nginx_pull(self):
        """
        Method is used to pull nginx latest version from docker hub
        """
        terminal_command = "docker pull nginx:latest"
        success_code = "Status: Image is up to date for nginx:latest"
        output_line = subprocess.getstatusoutput(terminal_command)
        output_line = output_line[1].split("\n")

        for line in output_line:
            if success_code in line:
                logging.info("Latest nginx was downloaded successfully.")
                return True
        logging.error("Can't download nginx:latest")

    def nginx_run(self):
        """
        Method is used to Run nginx container
        """
        terminal_command = "docker run --name '{}' -p 80:80 -d nginx".format(self.container_name)
        start_nginx = subprocess.getoutput(terminal_command)

    def nginx_validate(self):
        """
        Method is used to validate that nginx is running
        """
        terminal_command = "docker ps -a | grep '{}'".format(self.container_name)
        success_code = "Up"
        output_line = subprocess.getstatusoutput(terminal_command)
        output_line = output_line[1].split("\n")

        for line in output_line:
            if success_code in line:
                logging.info("nginx named '{}' is UP".format(self.container_name))
                return True
        logging.exception("Can't start nginx named '{}'.".format(self.container_name))

    def nginx_install(self):
        """
        Method is used to prepare environment for testing
        """
        self.check_previous_nginx_instance()
        self.nginx_pull()
        self.nginx_run()
        self.nginx_validate()

    def set_method_request(self):
        """
        This method is used to send HTTP REQUEST packet to nginx
        """
        logging.info("Sending HTTP REQUEST request to '{}'.".format(self.nginx_ip))
        send = requests.request("POST", self.nginx_ip)
        message = "REQUEST"
        self.validate_http(send, message)

    def set_method_get(self):
        """
        This method is used to send HTTP GET packet to nginx
        """
        logging.info("Sending HTTP GET request to '{}'.".format(self.nginx_ip))
        send = requests.get(self.nginx_ip)
        message = "GET"
        self.validate_http(send, message)

    def set_method_post(self):
        """
        This method is used to send HTTP POST packet to nginx
        """
        logging.info("Sending HTTP POST request to '{}'.".format(self.nginx_ip))
        send = requests.post(self.nginx_ip)
        message = "POST"
        self.validate_http(send, message)

    def set_user_agent(self):
        """
        This method is used to send HTTP packet with custom 'User-Agent' (Browser) from dictionary to nginx
        """
        for agent in self._http_headers["User-Agent"]:
            logging.info(
                "Sending HTTP request with User Agent '{}' to '{}'".format(agent, self.nginx_ip))
            send = requests.get(self.nginx_ip, headers={'User-Agent': agent})
            message = "with User Agent '{}'".format(agent)
            self.validate_http(send, message)

    def set_http_version(self):
        """
        This method is used to send HTTP packet with custom 'HTTP-VERSION' from dictionary to nginx
        """
        for version in self._http_headers["HTTP Version"]:
            logging.info(
                "Sending HTTP request with Version '{}' to '{}'".format(version, self.nginx_ip))
            send = requests.get(self.nginx_ip, headers={'Request Version': version})
            message = "with Version '{}'".format(version)
            self.validate_http(send, message)

    def set_large_header(self):
        """
        This method is used to send HTTP packet with custom 'HEADER-SIZE'
        """
        logging.info("Sending HTTP with Header size 35K request to '{}'.".format(self.nginx_ip))
        large_header = self.generate_random_str()
        send = requests.get(self.nginx_ip, headers={'User-Agent': large_header})
        message = "with Header size 35K"
        self.validate_http(send, message)

    def send_packets_http(self):
        """
        This method is used to gather all http requests and spam nginx
        """
        self.set_method_request()
        self.set_method_get()
        self.set_method_post()
        self.set_user_agent()
        self.set_http_version()
        self.set_large_header()

    @staticmethod
    def generate_random_str(length=35000):
        """
        Generate random string with 'hardcoded' 35000 bytes
        :param length: bytes in string
        :return: randomly generated string
        """
        return ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(length))

    def validate_http(self, send, message):
        """
        General method to validate status of http request
        :param send: http request
        :param message: type of http packet (method)
        :return: status
        """
        received = send.status_code

        if received == self.success_http_code:
            logging.info("HTTP request '{}' was successful to '{}' with status '{}'.".format(
                message, self.nginx_ip, received))
        else:
            logging.error("HTTP request '{}' was FAILED to '{}' with status '{}'.".format(
                message, self.nginx_ip, received))
        send.close()
        return send

    @staticmethod
    def validate_sudo(must=True):
        """
        This func checks whether the user running the process has sudo privileges.
        :param: must: if the user must be sudo, and he\she is not, raise an error.
        :return: 1 if yes (True), 0 if not (False).
        """
        user = os.getenv("SUDO_USER")
        if user is None:
            if must is True:
                logging.error("Sudo privileges are required!")
                raise Exception("Sudo privileges are required!")
            else:
                logging.warning("This user doesn't have sudo privileges.")
                return 0
        return 1


def main():
    docker_test = NginxTest()
    docker_test.check_docker_status()
    docker_test.nginx_install()
    docker_test.send_packets_http()


if __name__ == '__main__':
    main()
