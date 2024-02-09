# Use the official MySQL image as a parent image
FROM mysql:8

# Set environment variables
ENV MYSQL_DATABASE=labelbase
ENV MYSQL_USER=ulabelbase
ENV MYSQL_PASSWORD=vrZvZmX6Kp16B9tTa8JAA4RtAkWEhi
ENV MYSQL_ROOT_PASSWORD=iheWkAtR4AAJ8aTt9B61pK6XmZvZrv


COPY init.sql /docker-entrypoint-initdb.d/init.sql
