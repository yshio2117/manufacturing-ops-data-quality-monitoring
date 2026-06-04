FROM python:3.12-slim

WORKDIR /app

# install python deps
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip \
  && pip install --no-cache-dir -r requirements.txt

COPY config/ config/
COPY sql/ sql/
COPY src/ src/
COPY data/ data/

ENV PYTHONPATH=/app

# run for BigQuery output
#CMD ["python", "-m", "src.manufacturing_ops.main", "--input-file", "data/input/sample_manufacturing_shift_logs.csv", "--output", "bigquery"]

# run for local output
CMD ["python", "-m", "src.manufacturing_ops.main", "--input-file", "data/input/sample_manufacturing_shift_logs.csv", "--output", "local"]