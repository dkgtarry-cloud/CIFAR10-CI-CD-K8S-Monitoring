FROM python:3.14-slim

WORKDIR /app

COPY . /app

RUN pip install --upgrade pip && \
    pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu && \
    pip install flask pillow --no-cache-dir


EXPOSE 5000

CMD ["python","app.py"]