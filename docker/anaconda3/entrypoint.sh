#!/bin/sh

# Set the timezone. Base image does not contain the setup-timezone script, so an alternate way is used.
if [ -n "$TIMEZONE" ]; then
    cp /usr/share/zoneinfo/${TIMEZONE} /etc/localtime && \
	echo "${TIMEZONE}" >  /etc/timezone && \
	echo "Container timezone set to: $TIMEZONE"
else
	echo "Container timezone not modified"
fi

echo "Starting jyputer notebook ..."

jupyter notebook --notebook-dir=/opt/notebooks --NotebookApp.allow_origin='*' --ip='*' --port=8888 --no-browser --NotebookApp.token='' --allow-root
