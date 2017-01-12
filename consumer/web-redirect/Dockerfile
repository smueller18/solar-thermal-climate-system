FROM smueller18/base:python3-kafka

MAINTAINER smueller18

COPY src /opt/web-redirect

EXPOSE 5002

WORKDIR /opt/web-redirect

CMD ["python", "consumer_web_redirect.py"]
