FROM smueller18/python3-kafka:psycopg2

MAINTAINER smueller18

COPY src /opt/postgres

WORKDIR /opt/postgres

CMD ["python", "database_writer.py"]
