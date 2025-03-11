pipeline {
    agent any
    environment {
        SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8' // Jenkins SSH credential ID
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '3.111.252.210'
        LOCAL_JSON_FILE = "db_config.json" // JSON file stored in Jenkins workspace
        REMOTE_JSON_PATH = "/home/thahera/db_config.json"
        MYSQL_USER = "root"
        MYSQL_PASSWORD = "AlgoTeam123" // MySQL password
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo "Checking out code from Git repository..."
                    checkout scm // Pulls the latest code (including db_config.json)
                }
            }
        }

        stage('Upload JSON to Remote Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                    echo "Uploading JSON file to remote server..."
                    scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_JSON_FILE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_JSON_PATH}
                    """
                }
            }
        }

        stage('Generate SQL Dump Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                    echo "Connecting to ${REMOTE_HOST} to generate scripts..."
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} <<'EOF'

                    echo "Successfully logged in!"
                    cd /home/thahera/

                    # Run Python script to process JSON and generate MySQL dumps
                    python3 <<EOPYTHON
import json
import os

# Read JSON file from remote server
json_file = "${REMOTE_JSON_PATH}"
with open(json_file, "r") as file:
    data = json.load(file)

# Define MySQL credentials
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

# Loop through entries to generate dump scripts
for entry in data:
    db_name = entry["database"]
    table_name = entry["table"]
    option = entry["option"].strip().lower()
    where_condition = entry.get("where_condition", None)

    # Define filename with timestamp
    timestamp = os.popen("date +%d_%m_%y").read().strip()
    dump_file = f"{table_name}_{timestamp}.sql"

    # Choose dump type
    dump_command = None
    if option == "data":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db_name} {table_name}"
    elif option == "structure":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db_name} {table_name}"
    elif option == "both":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name}"

    # If WHERE condition exists, format it correctly
    if dump_command and where_condition:
        where_condition = where_condition.replace('"', '\\"')  # Escape double quotes
        dump_command += f' --where="{where_condition}"'

    # Execute dump command
    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        os.system(dump_command)
        print(f"Dump generated: {dump_file}")

print("Scripts generated successfully in /home/thahera/")
EOPYTHON

                    logout
                    EOF
                    """
                }
            }
        }
    }
}
