# Base image
FROM python:3.9

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project code into the container
COPY . /code/

# Run Django migrations (Added this step)
RUN python manage.py migrate

# Expose the server port
EXPOSE 8083

# Run the Django server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8083"]
