FROM python:3.8-slim
WORKDIR /opt/korto-exporter
ENV PYTHONPATH '/opt/korto-exporter/'

COPY requirements.txt /opt/korto-exporter/requirements.txt
RUN pip install -r /opt/korto-exporter/requirements.txt && \
    rm -f /opt/korto-exporter/requirements.txt
COPY src /opt/korto-exporter/src

CMD ["python" , "/opt/korto-exporter/src/collector.py"]
