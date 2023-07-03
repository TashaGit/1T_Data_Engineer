FROM postgres:latest
ENV POSTGRES_PASSWORD=password
ENV POSTGRES_DB=db
COPY /db/init.sql /docker-entrypoint-initdb.d/init.sql