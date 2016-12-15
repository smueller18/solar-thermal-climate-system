# Creation of self signed Certificate

```
openssl req \
        -x509 \
        -nodes \
        -newkey rsa:4096 \
        -keyout server.key \
        -out server.crt \
        -days 3650 \
        -config ./openssl-localhost.conf
```
