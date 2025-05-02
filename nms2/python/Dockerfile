FROM python:alpine

WORKDIR /python

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /python
COPY . .
 
# Command to run the application
CMD ["python3", "app.py"]
