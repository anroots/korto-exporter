FROM python:3.8
WORKDIR /opt/korto-exporter
ENV PYTHONPATH '/opt/korto-exporter/'
CMD ["python" , "/opt/korto-exporter/collector.py"]

COPY requirements.txt /opt/korto-exporter/requirements.txt
RUN pip install -r /opt/korto-exporter/requirements.txt
COPY src /opt/korto-exporter

