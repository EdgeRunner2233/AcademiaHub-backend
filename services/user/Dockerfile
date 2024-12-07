FROM python:3.12-slim

EXPOSE 30000

WORKDIR /Service/User

COPY . /Service/User

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip install -r requirements.txt

RUN sed -i 's/deb.debian.org/mirrors.tuna.tsinghua.edu.cn/g' /etc/apt/sources.list.d/debian.sources
RUN apt update && apt install gcc -y

CMD [ "bash", "start_server.sh" ]