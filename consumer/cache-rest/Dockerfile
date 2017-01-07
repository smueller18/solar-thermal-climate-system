FROM smueller18/base:python3-kafka

MAINTAINER smueller18

COPY src /opt/cache-rest

EXPOSE 5001

WORKDIR /opt/cache-rest

CMD ["python", "consumer_cache_rest.py"]
