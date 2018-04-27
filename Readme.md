**Count_Exporter for Prometheus**

This Exporter count Files in specified Paths, for each path a metric will return the Number of Files found.

Usage:
Before Starting the exporter, write a Config.txt like: 

MetricName Path 
...

Example  Config: See Config.txt File


Usage as Service (UNIX):

Edit the .service File, and put in the right Path of count_exporter.py File

Move .service File to /etc/systemd/system/

systemctl daemon-reload

systemctl enable count_exporter.service

systemctl start count_exporter.service

Usage as Service (Windows):

Prepare Service
https://stackoverflow.com/questions/32404/is-it-possible-to-run-a-python-script-as-a-service-in-windows-if-possible-how

Install Python for Windows
https://sourceforge.net/projects/pywin32/?source=typ_redirect

Install Python 2.7
https://www.python.org/downloads/release/python-2713/

Install required Packages with pip.exe
https://github.com/prometheus/client_python

In CMD type:

<Your python Path>\python.exe "Path to your script".py install
  
  oder
  
sc create FileCountExporter binpath= "C:\Python27\Python.exe C:\Users\PietschF\Desktop\count_exporter\count_exporter.py" DisplayName= "FileCountExporter" start= auto

Delete Service

sc delete "Service Name"



