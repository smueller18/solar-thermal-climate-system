FROM smueller18/python3-kafka:psycopg2

MAINTAINER smueller18

COPY src /consumer/postgres

WORKDIR /consumer/postgres

CMD ["python", "database_writer.py"]
