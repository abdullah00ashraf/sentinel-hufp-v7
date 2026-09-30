FROM python:3.11
WORKDIR /code
# Copy requirements first to leverage Docker cache
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
# Copy the entire project
COPY . /code
# Start the FastAPI server on port 7860 (Hugging Face standard)
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860"]