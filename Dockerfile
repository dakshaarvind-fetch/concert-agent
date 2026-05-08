FROM python:3.11-slim

WORKDIR /app

# git is required for GitHub-sourced uagents packages
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*

COPY agents/concierge/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["python", "agents/concierge/agent.py"]
