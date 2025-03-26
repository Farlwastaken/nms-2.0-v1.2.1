# Use Python 3.13.2 image
FROM python:3.13.2

# Set working directory to /python
WORKDIR /python

# Copy requirements and install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /python
COPY . .
 
# Command to run the Flask server and your main script
CMD ["python3", "app.py"]
