FROM python:3.9
WORKDIR /app
COPY server.py /app
RUN pip install flask mysql-connector-python
CMD ["python", "server.py"]
