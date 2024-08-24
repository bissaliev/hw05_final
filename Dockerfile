FROM mypython3.8-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY yatube/ /app
ENTRYPOINT [ "./run.sh" ]
