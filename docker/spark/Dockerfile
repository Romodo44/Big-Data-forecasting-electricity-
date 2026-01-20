FROM bitnami/spark:3.5.0-debian-11

USER root

RUN pip install --no-cache-dir \
    pandas \
    pyarrow \
    numpy \
    scipy \
    xgboost \
    joblib

USER 1001
