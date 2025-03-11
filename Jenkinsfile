pipeline {
    agent any
    environment {
        SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8' // Jenkins SSH credential ID
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '3.111.252.210' // Source instance
        DEST_HOST = '43.205.56.101'  // Destination instance
        LOCAL_EXCEL_FILE = "db_config.xlsx" // Excel file stored in Jenkins workspace
        REMOTE_EXCEL_PATH = "/home/thahera/db_config.xlsx"
        MYSQL_USER = "root"
        MYSQL_PASSWORD = "AlgoTeam123" // MySQL password
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo "Checking out code from Git repository..."
                    checkout scm // Pulls the latest code (including db_config.xlsx)
                }
            }
        }

        stage('Upload Excel to Remote Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                    echo "Uploading Excel file to remote server..."
                    scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_EXCEL_PATH}
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
                    
                    # Ensure required Python packages are installed
                    python3 -m pip install pandas openpyxl --user
                    
                    # Run Python script to process Excel and generate MySQL dumps
                    python3 <<EOPYTHON
import pandas as pd
import os

# Read Excel file from remote server
excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

# Define MySQL credentials
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

# Loop through rows to generate dump scripts
for index, row in df.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    # Define filename with timestamp
    timestamp = os.popen("date +%d_%m_%y_%H_%M_%S").read().strip()
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
    if dump_command and where_condition and where_condition.lower() != "nan":
        where_condition = where_condition.replace('"', '\\"')  # Escape quotes
        dump_command += f' --where="{where_condition}"'

    # Execute dump command
    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        os.system(dump_command)
        print(f"Dump file generated: {dump_file}")
EOPYTHON
                    
                    # Change ownership of generated SQL files
                    sudo chown ${REMOTE_USER}:${REMOTE_USER} /home/thahera/*.sql
                    
                    echo "Scripts generated successfully in /home/thahera/"
                    EOF
                    """
                }
            }
        }

        stage('Transfer and Set Permissions') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                    echo "Transferring generated scripts to ${DEST_HOST}..."
                    scp -o StrictHostKeyChecking=no /home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/
                    """
                }
            }
        }
    }
}
