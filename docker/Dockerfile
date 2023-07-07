FROM python:3.10-slim-buster

WORKDIR /usr/local/bin

RUN python3 -m pip install -U pandas numpy scikit-learn

COPY validate.py score.py .

RUN chmod +x validate.py &&\
    chmod +x score.py
