FROM python:3.12-slim

EXPOSE 30000

WORKDIR /Service/User

COPY . /Service/User

RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
RUN pip install -r requirements.txt

CMD [ "uwsgi", "uwsgi.ini" ]