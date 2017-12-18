FROM python:3

RUN apt-get update && apt-get -y install build-essential 

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

RUN make install

#RUN make test
CMD python meetme/meetme.py