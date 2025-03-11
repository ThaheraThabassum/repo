pipeline {
    agent any
    environment {
        SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8' // Jenkins SSH credential ID
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '3.111.252.210'
        LOCAL_EXCEL_FILE = "db_tables.xlsx"  // Excel file stored in Jenkins workspace
        REMOTE_EXCEL_PATH = "/home/thahera/db_tables.xlsx"
    }
    stages {
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

                    # Run Python script to process Excel and generate MySQL dumps
                    python3 <<EOPYTHON
import pandas as pd
import os

# Read Excel file from remote server
excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

# Loop through rows to generate dump scripts
for index, row in df.iterrows():
    db_name = row['database']
    table_name = row['table']
    option = row['option'].strip().lower()
    where_condition = row.get('where_condition', None)

    # Define filename with timestamp
    timestamp = "$(date +%Y%m%d)"
    dump_file = f"{table_name}_{timestamp}.sql"

    # Choose dump type
    dump_command = None
    if option == "data":
        dump_command = f"mysqldump -u root -p --no-create-info {db_name} {table_name}"
    elif option == "structure":
        dump_command = f"mysqldump -u root -p --no-data {db_name} {table_name}"
    elif option == "both":
        dump_command = f"mysqldump -u root -p {db_name} {table_name}"

    # If WHERE condition exists, format it correctly
    if dump_command and where_condition and pd.notna(where_condition):
        where_condition = where_condition.replace('"', '\\"')  # Escape quotes
        dump_command += f" --where=\"{where_condition}\""

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
