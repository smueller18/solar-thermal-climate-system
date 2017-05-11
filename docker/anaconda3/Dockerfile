FROM continuumio/anaconda3

MAINTAINER smueller18

RUN apt-get install -y gcc libpq-dev python3-dev \
    && pip install psycopg2 \
    && pip install tsfresh tabulate

EXPOSE 8888

CMD ["/bin/sh", "-c", "jupyter notebook --notebook-dir=/opt/notebooks --NotebookApp.allow_origin='*' --ip='*' --port=8888 --no-browser --NotebookApp.token=''"]
