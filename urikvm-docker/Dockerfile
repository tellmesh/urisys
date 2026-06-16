FROM python:3.12-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -e .
EXPOSE 8794
CMD ["urisys-kvm", "serve", "--host", "0.0.0.0", "--port", "8794"]
