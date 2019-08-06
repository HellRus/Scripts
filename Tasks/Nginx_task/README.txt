Exercise:

this is a basic python test that should run on any linux distribution (will be tested on ubuntu 16:04).

Create a python script that will
	a.Pull and Run the latest nginx version from docker hub (nginx:latest)
	b.Use python library to send HTTP Request to your running nginx and report the response
	c.Repeat step b:
            	i.	with different HTTP methods (GET, POST)
                ii.	user-agent (Chrome, Safari)
                iii.    different HTTP Versions
                iv.	large http header size > 32k
	d. generate a report with test results  -requests resulted with response code different than 200 OK will be marked as Failed.

* assume the python script and the docker daemon are running on the same host and docker is already installed and running.

At the end, i should receive a python script that will simply run without any configuration arguments
and will export a report to a different file named report.data.

bonus - use pythons's pytest framework to run your tests.
========================================================================================================================

Requirements (for Linux):
1) Download Docker and install it
2) Start a Docker on your system:
======================================================================================

Script run:
1) Script can be executed from shell on a host that have python3 (3.6+ version i assume) after all requirements are met:
    python3 nginx_test.py
1.5) OR (maybe should be started with root permissions, it's depending on the Docker settings/configuration)
sudo ./nginx_test.py
2) Log will be stored to same directory.
