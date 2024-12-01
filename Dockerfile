FROM python:3.11.8-slim

RUN apt-get update && apt-get install -y nodejs npm

WORKDIR /app

# Update pip
RUN pip install --upgrade pip

# Install pandas first
RUN pip install pandas>=1.2.3

# Install plotly explicitly
RUN pip install plotly>=5.0.0

# Install pandas first
RUN pip install pydantic>=2.3.0

# Now install other requirements
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install node dependencies
COPY package.json ./
RUN npm install

COPY . .

EXPOSE 8550
CMD ["gunicorn", "run:server", "-b", "0.0.0.0:8550"]