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
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} <<EOF
                        echo "Successfully logged in!"
                        cd /home/thahera/

                        echo "${SUDO_PASSWORD}" | sudo -S apt install -y python3-pandas python3-openpyxl

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

df = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
generated_files = []

for _, row in df.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    dump_file = f"{table_name}_{timestamp}.sql"
    dump_command = None
    if option == "data":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db_name} {table_name}"
    elif option == "structure":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db_name} {table_name}"
    elif option == "both":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name}"
    
    if dump_command and where_condition and where_condition.lower() != "nan":
        dump_command += f' --where="{where_condition.replace("\"", "\\\"")}"'
    
    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        os.system(dump_command)
        print(f"Dump generated: {dump_file}")
        generated_files.append(dump_file)

print(f"Generated Files: {generated_files}")
EOPYTHON
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
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'echo "${SUDO_PASSWORD}" | sudo -S chmod 777 /home/thahera/*.sql'
                    """
                }
            }
        }

        stage('Backup and Load Data') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Performing backup and loading data on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<EOF
                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

databases = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
transferred_files = [f for f in os.listdir("/home/thahera/") if f.endswith(".sql")]

for _, row in databases.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    check_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}';"
    result = os.popen(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -N -e '{check_query}'").read().strip()

    if result == "1":
        backup_table = f"{table_name}_{timestamp}"
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"CREATE TABLE {db_name}.{backup_table} AS SELECT * FROM {db_name}.{table_name};\"")
    
    if result == "1" and where_condition and where_condition.lower() != "nan":
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"DELETE FROM {db_name}.{table_name} WHERE {where_condition};\"")
    
    sql_file_name = next((file for file in transferred_files if file.startswith(f"{table_name}_{timestamp}")), None)
    if sql_file_name:
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} -e \"SOURCE /home/thahera/{sql_file_name};\"")
EOPYTHON
                        EOF
                    """
                }
            }
        }
    }
}
