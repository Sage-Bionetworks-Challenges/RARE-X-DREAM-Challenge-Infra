FROM python:3.10-slim-buster

WORKDIR /usr/local/bin

RUN python3 -m pip install -U pandas numpy scikit-learn

COPY base_model.py .

RUN chmod +x base_model.py

# Set the main command of the image.
# We recommend using this form instead of `ENTRYPOINT command param1`.
ENTRYPOINT ["python", "base_model.py"]