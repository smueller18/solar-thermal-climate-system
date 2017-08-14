FROM continuumio/anaconda3

MAINTAINER smueller18

#RUN apt install -y aptitude
RUN apt update && apt upgrade -y

RUN apt install -y gcc libpq-dev python3-dev graphviz \
    && pip install psycopg2 \
    && pip install tsfresh tabulate pydotplus

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh
RUN mkdir -p /opt/notebooks

EXPOSE 8888

CMD ["/usr/local/bin/entrypoint.sh"]
