FROM python:3.11.8-slim

RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

COPY requirements.txt .
RUN pip install -r requirements.txt

# Output the version of dash-mantine-components
RUN pip show dash-mantine-components

COPY package.json package-lock.json ./
RUN npm install

COPY . .

EXPOSE 8550
CMD ["gunicorn", "run:server", "-b", "0.0.0.0:8550"]
