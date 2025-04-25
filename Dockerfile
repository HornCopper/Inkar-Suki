FROM inkar-base:latest

WORKDIR /app
COPY . .
RUN pip install .
CMD ["nb", "run"]