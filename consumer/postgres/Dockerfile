FROM smueller18/base:python3-kafka

MAINTAINER smueller18

COPY src /opt/postgres

WORKDIR /opt/postgres

CMD ["python", "database_writer.py"]
