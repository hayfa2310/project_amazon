FROM python:3.7
COPY . /app
WORKDIR /app
RUN apt-get update
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["main_app.py"]