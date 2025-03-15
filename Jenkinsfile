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

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

generated_files = []

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
        generated_files.append(dump_file)

print("Scripts generated successfully in /home/thahera/")
print(f"Timestamp used: {timestamp}")
print(f"Generated Files: {generated_files}")

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

        stage('Backup and Load Data') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Performing backup and loading data on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        echo "Processing tables for backup and data loading..."

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

databases = pd.read_excel("${REMOTE_EXCEL_PATH}")

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

# List of transferred SQL files
transferred_files = os.listdir("/home/thahera/")
transferred_files = [f for f in transferred_files if f.endswith(".sql")]

for index, row in databases.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    check_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}';"
    check_command = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -N -e '{check_query}'"
    result = os.popen(check_command).read().strip()

    if result == "1":
        print(f"✅ Table '{table_name}' exists in '{db_name}', taking backup...")
        backup_table = f"{table_name}_{timestamp}"
        backup_query = f"CREATE TABLE {db_name}.{backup_table} AS SELECT * FROM {db_name}.{table_name};"
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"{backup_query}\"")
        print(f"Backup created: {backup_table}")
    else:
        print(f"❌ Table '{table_name}' does not exist, skipping backup.")

    if result == "1" and where_condition and where_condition.lower() != "nan":
        if option == "structure":
            drop_query = f"DROP TABLE {db_name}.{table_name};"
            os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"{drop_query}\"")
            print(f"Table {db_name}.{table_name} dropped.")
        else:
            delete_query = f"DELETE FROM {db_name}.{table_name} WHERE {where_condition};"
            os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"{delete_query}\"")
            print(f"Data deleted from {db_name}.{table_name} where {where_condition}")
    elif result == "1":
        if option == "structure":
            drop_query = f"DROP TABLE {db_name}.{table_name};"
            os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e \"{drop_query}\"")
            print(f"Table {db_name}.{table_name} dropped.")

    # Find the corresponding SQL file and source it
    sql_file_name = next((file for file in transferred_files if file.startswith(f"{table_name}_{timestamp}")), None)

    if sql_file_name:
        sql_file = f"/home/thahera/{sql_file_name}"
        source_query = f"SOURCE {sql_file};"
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} -e \"{source_query}\"")
        print(f"Data sourced from {sql_file}")
    else:
        print(f"❌ SQL file not found for {table_name}, skipping sourcing.")

EOPYTHON

                        EOF
                    """
                }
            }
        }
    }
}
