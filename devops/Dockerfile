FROM python:3.8-slim AS compile-image

RUN apt-get update

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.8-slim AS build-image

COPY --from=compile-image /root/.local /root/.local
COPY app.py/ .

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]