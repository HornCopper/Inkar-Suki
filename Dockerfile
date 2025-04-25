FROM registry.cn-hangzhou.aliyuncs.com/hzzz9/inkar-base:latest

WORKDIR /app
COPY . .
RUN pip install .
CMD ["nb", "run"]