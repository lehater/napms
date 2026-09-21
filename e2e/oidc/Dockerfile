FROM python:3.12-slim
WORKDIR /srv
RUN python -m pip install --no-cache-dir "PyJWT[crypto]>=2.10,<3"
COPY server.py ./
EXPOSE 8443
CMD ["python", "server.py"]
