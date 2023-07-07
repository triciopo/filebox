FROM python:3.11-slim

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./filebox /app/filebox

CMD ["uvicorn", "filebox.main:app", "--workers", "1", "--host", "0.0.0.0", "--port", "8000"]
