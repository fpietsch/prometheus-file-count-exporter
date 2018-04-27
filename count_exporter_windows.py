#!/usr/bin/env python
import os
import json
from argparse import ArgumentParser
from prometheus_client import start_http_server, Metric, REGISTRY
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily
import time
import logging, logging.handlers
import sys
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

PORT = 9888  # Metrik-Endpoint Port for calling "ip:PORT/metrics"
UPDATE_INTERVAL = 10  # in seconds

debug = False
files = {}
states = {}
config = "./config.txt"
logger = logging.getLogger('FileCountExporter')
base_dir = os.path.dirname('C:\\Users\\PietschF\\Desktop\\count_exporter\\')

def count_files_in_path(path):
	#logger.debug("Count Files in %s "% (path))
	num_files = len([f for f in os.listdir(path)if os.path.isfile(os.path.join(path, f))])
	return num_files

def read_config(path):
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
                #logger.debug("Update State for %s: %s"%(name,state))
		states[name] = count_files_in_path(files[name])
	return
    
class CustomCollector(object):
    def collect(self):
        c = GaugeMetricFamily('file_count', 'Filescount in Path', labels=[
                                'name'])
        for name, state in states.items():
            c.add_metric(['%s' % name], int(state))
        yield c

class AppServerSvc (win32serviceutil.ServiceFramework):
    _svc_name_ = "FileCountExporter"
    _svc_display_name_ = "FileCountExporter"

    def __init__(self,args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        self.hWaitStop = win32event.CreateEvent(None,0,0,None)
        #socket.setdefaulttimeout(60)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.stop = True

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
        self.timeout = 1000
        config = os.path.join(base_dir, "config.txt")
        servicemanager.LogInfoMsg('Starting with Config.txt from %s'%config)
        #logger.info('Read Config.txt from %s'%config)
        read_config(config)
        #logger.info('Start Http Server on Port %s'%PORT)
        servicemanager.LogInfoMsg('Start Http Server on Port %s'%PORT)
        start_http_server(int(PORT))
        REGISTRY.register(CustomCollector())
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()

    def main(self):
        while 1:
                rc = win32event.WaitForSingleObject(self.hWaitStop, self.timeout)
                #logger.debug('Update Matches')
                if rc == win32event.WAIT_OBJECT_0:
                        servicemanager.LogInfoMsg("STOPPED!")
                        break
                else:
                        update_matches()
                        time.sleep(UPDATE_INTERVAL)
                 
if __name__ == '__main__':
    logger.setLevel(logging.DEBUG)
    # create console handler and set level to debug
    #dllname = os.path.join(base_dir, "win32service.pyd")
    #ch = logging.handlers.NTEventLogHandler("FileCountExporter Logging", dllname=dllname)
    #ch.setLevel(logging.DEBUG)
    # create formatter
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # add formatter to ch
    #ch.setFormatter(formatter)
    # add ch to logger
    #logger.addHandler(ch)
    # Start Http Server, waiting for Prometheus Pulls
    win32serviceutil.HandleCommandLine(AppServerSvc)
