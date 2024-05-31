FROM mypython3.8-slim
WORKDIR /app
COPY ./requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir
COPY yatube/ /app
# CMD [ "python3", "manage.py", "runserver", "0:8000" ]
CMD [ "gunicorn", "--bind", "0:8000", "yatube.wsgi" ]

