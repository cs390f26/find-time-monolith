#!/bin/bash

# Exit if a command fails, an undefined variable is used,
# or a command in a pipeline fails.
set -euo pipefail

APP_DIR="/opt/find-a-time"
DB_DATA_DIR="/var/lib/find-a-time-dynamodb"
ENV_FILE="/etc/find-a-time.env"

# The strings are split so they are copied as plain shell text.
REPO_URL="https:""//github.com/cs390f26/find-time-monolith.git"
DB_URL="http:""//127.0.0.1:8000"
WEB_HEALTH_URL="http:""//127.0.0.1:5000/health"

echo "Starting Find a Time deployment..."

# ------------------------------------------------------------
# 1. Install operating-system dependencies.
# ------------------------------------------------------------

dnf install -y \
    git \
    python3.12 \
    python3.12-pip \
    java-17-amazon-corretto-headless
# ------------------------------------------------------------
# 2. Clone the application from GitHub.
# ------------------------------------------------------------

git clone \
    --branch main \
    --single-branch \
    "$REPO_URL" \
    "$APP_DIR"

# The application services run as ec2-user.
chown -R ec2-user:ec2-user "$APP_DIR"

# ------------------------------------------------------------
# # ------------------------------------------------------------
# 3. Download DynamoDB Local.
# ------------------------------------------------------------

mkdir -p "$APP_DIR/db"

curl -L \
    "https://d1ni2b6xgvw0s0.cloudfront.net/dynamodb_local_latest.tar.gz" \
    -o /tmp/dynamodb_local_latest.tar.gz

tar -xzf \
    /tmp/dynamodb_local_latest.tar.gz \
    -C "$APP_DIR/db"

rm /tmp/dynamodb_local_latest.tar.gz

chown -R ec2-user:ec2-user "$APP_DIR/db"
# ------------------------------------------------------------
# 4. Create the Python virtual environment and install the app.
# ------------------------------------------------------------

sudo -u ec2-user \
    /usr/bin/python3.12 -m venv "$APP_DIR/.venv"

sudo -u ec2-user \
    "$APP_DIR/.venv/bin/pip" install \
    -r "$APP_DIR/requirements.txt"

sudo -u ec2-user \
    "$APP_DIR/.venv/bin/pip" install \
    -e "$APP_DIR"
# ------------------------------------------------------------
# 5. Create persistent storage for DynamoDB Local.
# ------------------------------------------------------------

install \
    -d \
    -o ec2-user \
    -g ec2-user \
    "$DB_DATA_DIR"

# ------------------------------------------------------------
# 5. Create the application environment configuration.
# ------------------------------------------------------------

cat > "$ENV_FILE" <<EOF_ENV
AWS_ACCESS_KEY_ID=local
AWS_SECRET_ACCESS_KEY=local
AWS_DEFAULT_REGION=us-east-1
FIND_A_TIME_TABLE_NAME=FindATime
DYNAMODB_ENDPOINT_URL=$DB_URL
EOF_ENV

chown root:ec2-user "$ENV_FILE"
chmod 640 "$ENV_FILE"

# Load the same settings for the setup scripts.
set -a
source "$ENV_FILE"
set +a

# ------------------------------------------------------------
# 7. Install the systemd service definitions.
# ------------------------------------------------------------

cp \
    "$APP_DIR/deploy/find-a-time-db.service" \
    /etc/systemd/system/find-a-time-db.service

cp \
    "$APP_DIR/deploy/find-a-time-web.service" \
    /etc/systemd/system/find-a-time-web.service

systemctl daemon-reload

systemctl enable find-a-time-db.service
systemctl enable find-a-time-web.service

# ------------------------------------------------------------
# 8. Start DynamoDB Local.
# ------------------------------------------------------------

systemctl start find-a-time-db.service

# Wait until DynamoDB Local accepts connections.
DB_READY=false

for attempt in {1..30}; do
    if curl \
        --silent \
        --output /dev/null \
        "$DB_URL"
    then
        DB_READY=true
        break
    fi

    sleep 1
done

if [ "$DB_READY" != "true" ]; then
    echo "DynamoDB Local did not become ready."
    exit 1
fi

echo "DynamoDB Local is ready."

# ------------------------------------------------------------
# 9. Create the table and load the approved sample data.
# ------------------------------------------------------------

cd "$APP_DIR"

"$APP_DIR/.venv/bin/python" scripts/create_table.py
"$APP_DIR/.venv/bin/python" scripts/seed_data.py

# ------------------------------------------------------------
# 10. Start the Gunicorn web service.
# ------------------------------------------------------------

systemctl start find-a-time-web.service

# ------------------------------------------------------------
# 10. Verify that the complete application is responding.
# ------------------------------------------------------------

WEB_READY=false

for attempt in {1..30}; do
    if curl \
        --fail \
        --silent \
        "$WEB_HEALTH_URL"
    then
        WEB_READY=true
        echo
        break
    fi

    sleep 1
done

if [ "$WEB_READY" != "true" ]; then
    echo "Find a Time web application did not become ready."
    exit 1
fi

echo "Find a Time deployment completed successfully."
