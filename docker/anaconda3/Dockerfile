FROM continuumio/anaconda3

MAINTAINER smueller18

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

RUN apt-get install -y gcc libpq-dev python3-dev \
    && pip install psycopg2 \
    && pip install tsfresh tabulate pydotplus

EXPOSE 8888

ENTRYPOINT ["sh", "/usr/local/bin/entrypoint.sh"]

CMD ["/bin/sh", "-c", "jupyter notebook --notebook-dir=/opt/notebooks --NotebookApp.allow_origin='*' --ip='*' --port=8888 --no-browser --NotebookApp.token=''"]
