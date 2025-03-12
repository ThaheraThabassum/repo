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
                        echo "Generating SQL dump files on ${REMOTE_HOST}..."
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

    dump_file = f"/home/thahera/{table_name}_{timestamp}.sql"
    generated_files.append(dump_file)

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
        dump_command += f" > {dump_file}"
        os.system(dump_command)
        print(f"Dump generated: {dump_file}")

with open("/home/thahera/generated_sql_files.txt", "w") as f:
    f.write("\\n".join(generated_files))

print("Scripts generated successfully.")
print(f"Timestamp used: {timestamp}")
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

                        echo "Transferring list of generated SQL files..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/generated_sql_files.txt ${REMOTE_USER}@${DEST_HOST}:/home/thahera/

                        echo "Setting permissions for transferred files..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'echo "${SUDO_PASSWORD}" | sudo -S chmod 777 /home/thahera/*.sql'
                    """
                }
            }
        }

        stage('Backup, Delete Data, and Restore') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Processing databases on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        echo "Successfully logged into ${DEST_HOST}"
                        cd /home/thahera/

                        echo '${SUDO_PASSWORD}' | sudo -S apt install python3-pandas python3-openpyxl -y

                        python3 <<EOPYTHON
import pandas as pd
import os

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

# Read generated SQL filenames
with open("/home/thahera/generated_sql_files.txt", "r") as f:
    sql_files = {os.path.basename(line.strip()): line.strip() for line in f.readlines()}

for index, row in df.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    where_condition = str(row.get("where_condition", "")).strip()

    sql_filename = None
    for key in sql_files:
        if key.startswith(f"{table_name}_"):
            sql_filename = sql_files[key]
            break

    if sql_filename is None:
        print(f"Error: No matching SQL file found for table {table_name}. Skipping...")
        continue

    backup_table = f"{table_name}_backup"

    verify_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; SHOW TABLES LIKE \\'{backup_table}\\';'"
    if os.system(verify_cmd) != 0:
        backup_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; CREATE TABLE {backup_table} AS SELECT * FROM {table_name};'"
        os.system(backup_cmd)
        print(f"Backup created successfully: {backup_table}")
    else:
        print(f"Table {backup_table} already exists. No backup taken.")

    if where_condition and where_condition.lower() != "nan":
        delete_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; DELETE FROM {table_name} WHERE {where_condition};'"
        os.system(delete_cmd)
        print(f"Deleted data from {table_name} where {where_condition}")

    source_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < {sql_filename}"
    os.system(source_cmd)
    print(f"Sourced script: {sql_filename}")

    cleanup_cmd = f"ls -t /home/thahera/{table_name}_*.sql | tail -n +4 | xargs rm -f"
    os.system(cleanup_cmd)
    print("Cleaned up older backups.")

print("Database operations completed.")
EOPYTHON
                        EOF
                    """
                }
            }
        }
    }
}
