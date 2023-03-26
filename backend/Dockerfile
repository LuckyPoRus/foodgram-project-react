FROM python:3.10.10

WORKDIR /app

COPY . .

RUN python -m pip install --upgrade pip

RUN pip install -r /app/requirements.txt --no-cache-dir

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]