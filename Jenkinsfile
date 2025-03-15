pipeline {
    agent any

    environment {
        SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8'
        REMOTE_USER = 'thahera'
        REMOTE_HOST = '3.111.252.210'
        DEST_HOST = '43.205.56.101'
        LOCAL_EXCEL_FILE = "db_config.xlsx"
        REMOTE_EXCEL_PATH = "/home/thahera/db_config.xlsx"
        MYSQL_USER = "root"
        MYSQL_PASSWORD = "AlgoTeam123"
        SUDO_PASSWORD = "1234"
        TRANSFERRED_SCRIPTS = "/home/thahera/transferred_scripts.txt"
    }

    stages {
        stage('Checkout Code') {
            steps {
                script {
                    echo "Checking out code from Git repository..."
                    checkout scm
                }
            }
        }

        stage('Upload Excel to Remote Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Uploading Excel file to remote server..."
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
                    """
                }
            }
        }

        stage('Backup, Delete & Load Data') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Processing tables for backup, deletion, and data loading on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

databases = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    script_files = [line.strip() for line in f.readlines()]

for index, row in databases.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    check_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}';"
    check_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check_query}"'
    result = os.popen(check_command).read().strip()

    if result == "1":
        print(f"✅ Table '{table_name}' exists in '{db_name}', taking backup...")
        backup_table = f"{table_name}_backup_{timestamp}"

        backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE {db_name}.{backup_table} AS SELECT * FROM {db_name}.{table_name};"'
        os.system(backup_command)
        print(f"✅ Backup created: {backup_table}")

        # DELETE COMMAND (Handles where_condition)
        if where_condition and where_condition.lower() != "nan":
            delete_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DELETE FROM {db_name}.{table_name} WHERE {where_condition};"'
        else:
            delete_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DELETE FROM {db_name}.{table_name};"'

        os.system(delete_command)
        print(f"🚨 Deleted data from {db_name}.{table_name} with condition: {where_condition if where_condition else 'FULL DELETE'}")

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}")
        print(f"✅ Sourced script: {script_file}")
        script_files.remove(script_file)

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_files) + "\\n")

EOPYTHON

                        logout
                        EOF
                    """
                }
            }
        }
    }
}
