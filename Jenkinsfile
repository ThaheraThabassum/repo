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
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
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

                        echo '${SUDO_PASSWORD}' | sudo -S apt install python3-pandas python3-openpyxl -y

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S") # Generate timestamp here.

for index, row in df.iterrows():
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
        where_condition = where_condition.replace('"', '\\"')
        dump_command += f' --where="{where_condition}"'

    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        os.system(dump_command)
        print(f"Dump generated: {dump_file}")

print("Scripts generated successfully in /home/thahera/")
print(f"Timestamp used: {timestamp}") # Print the timestamp

EOPYTHON

                        logout
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

                        echo "Setting permissions for transferred files..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'echo "${SUDO_PASSWORD}" | sudo -S chmod 777 /home/thahera/*.sql'
                    """
                }
            }
        }

        stage('MySQL Operations') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Performing MySQL operations on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        echo '${SUDO_PASSWORD}' | sudo -S apt install python3-pandas python3-openpyxl -y
                        cd /home/thahera/

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime
import subprocess

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

def get_latest_dump_file(table_name):
    files = [f for f in os.listdir("/home/thahera/") if f.startswith(table_name) and f.endswith(".sql")]
    files.sort(key=lambda x: os.path.getmtime(os.path.join("/home/thahera/", x)), reverse=True)
    return files[0] if files else None

for index, row in df.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    action = str(row.get("action", "")).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    if action == "backup":
        backup_file = f"{table_name}_backup_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.sql"
        backup_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name} > /home/thahera/{backup_file}"
        os.system(backup_command)
        print(f"Backup created: {backup_file}")

        backups = [f for f in os.listdir("/home/thahera/") if f.startswith(f"{table_name}_backup_") and f.endswith(".sql")]
        backups.sort(key=lambda x: os.path.getmtime(os.path.join("/home/thahera/", x)), reverse=True)
        for old_backup in backups[4:]:
            os.remove(os.path.join("/home/thahera/", old_backup))
            print(f"Deleted old backup: {old_backup}")

    if action == "delete":
        delete_command = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'DELETE FROM {db_name}.{table_name}'"
        if where_condition and where_condition.lower() != "nan":
            where_condition = where_condition.replace('"', '\\"')
            delete_command += f" -e 'DELETE FROM {db_name}.{table_name} WHERE {where_condition}'"
        os.system(delete_command)
        print(f"Content deleted from {table_name}")

    if action == "restore":
        dump_file = get_latest_dump_file(table_name)
        if dump_file:
            restore_command = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{dump_file}"
            os.system(restore_command)
            print(f"Restored from: {dump_file}")
        else:
            print(f"No dump file found for {table_name}")

EOPYTHON

                        logout
                        EOF
                    """
                }
            }
        }
    }
}
