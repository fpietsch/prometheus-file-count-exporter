#!/usr/bin/env python
import os
import json
from argparse import ArgumentParser
from prometheus_client import start_http_server, Metric, REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import time
import logging
import sys

PORT = 9666  # Metrik-Endpoint Port for calling "ip:PORT/metrics"
UPDATE_INTERVAL = 10  # in seconds

debug = False
files = {}
states = {}
config = "./config.txt"

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true',
                        help='Activate Debug Output on stdout')
    parser.add_argument('config', help='Path of Config File',nargs='?')	
    args = parser.parse_args()
    if args.config is None:
        args.config = "./config.txt"
    return args

def count_files_in_path(path):
	if debug:
			print "Count Files in %s "%path
	num_files = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
	return num_files

def read_config(path):
	if debug:
			print "Open Config %s"%(path)
	file = open(path,"r+")
	lines = file.readlines()
	for line in lines:
		if len(line.split()) < 2:
			sys.exit("Error in Config File!")
		path = line.split()[1]
		name = line.split()[0]
		files[name] = path
		states[name] = 0
	return 

def update_matches():
	for name, state in states.items():
		states[name] = count_files_in_path(files[name])
		if debug:
			print "Update State for %s: %s"%(name,state)
	return
    
class CustomCollector(object):
    def collect(self):
        c = GaugeMetricFamily('file_count', 'Filescount in Path', labels=[
                                'name'])
        for name, state in states.items():
            if debug:
                print "Collect State for %s: %s"%(name,state)
            c.add_metric(['%s' % name], int(state))
        yield c

class StreamToLogger(object):
    """
    Fake file-like stream object that redirects writes to a logger instance.
    """

    def __init__(self, logger,terminal, log_level=logging.INFO):
        self.terminal = terminal
        self.logger = logger
        self.log_level = log_level
        self.linebuf = ''

    def write(self, buf):
        self.terminal.write(buf)
        for line in buf.rstrip().splitlines():
            self.logger.log(self.log_level, line.rstrip())
            #self.terminal.write(line)

    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        filename="out.log",
        filemode='a'
    )


if __name__ == '__main__':
    args = parse_args()
    if args.debug:
        debug = True
	config = args.config
    read_config(config)
    # Set Logger to Stdout and Stderror
    stdout_logger = logging.getLogger('STDOUT')
    sl = StreamToLogger(stdout_logger, sys.stdout, logging.INFO)
    sys.stdout = sl
    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, sys.stderr, logging.ERROR)
    sys.stderr = sl
    update_matches()
    print "Start Listening on Port %s" % PORT
    # Start Http Server, waiting for Prometheus Pulls
    start_http_server(int(PORT))
    REGISTRY.register(CustomCollector())
    while True:
        update_matches()
        time.sleep(UPDATE_INTERVAL)
