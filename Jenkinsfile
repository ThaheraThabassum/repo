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

        stage('Generate and Transfer SQL Scripts') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Generating SQL scripts on ${REMOTE_HOST}..."
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
print(f"Timestamp used: {timestamp}")

EOPYTHON

                        EOF

                        echo "Transferring generated SQL scripts to ${DEST_HOST}..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/

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
import datetime

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = None

for filename in os.listdir("/home/thahera"):
    print(f'filename:{filename}')
    if filename.endswith(".sql"):
        parts = filename.split("_")
        if len(parts) >= 5:
            timestamp = "_".join(parts[-4:])[:-4]
            break

if timestamp is None:
    print("Error: No SQL files found.")
else:
    print(f"Timestamp used: {timestamp}")

    for index, row in df.iterrows():
        db_name = row["database"]
        table_name = row["table"]
        where_condition = str(row.get("where_condition", "")).strip()

        check_table_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; SHOW TABLES LIKE \\'{table_name}\\';'"
        table_exists = os.system(check_table_cmd) == 0

        if not table_exists:
            print(f"Table {table_name} does not exist. Skipping backup and restore.")
            continue

        backup_table = f"{table_name}_{timestamp}"
        backup_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; CREATE TABLE {backup_table} AS SELECT * FROM {table_name};'"
        os.system(backup_cmd)
        print(f"Backup created: {backup_table}")

        if where_condition and where_condition.lower() != "nan":
            delete_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; DELETE FROM {table_name} WHERE {where_condition};'"
            os.system(delete_cmd)
            print(f"Deleted data from {table_name} where {where_condition}")

        script_file = f"/home/thahera/{table_name}_{timestamp}.sql"
        source_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < {script_file}"
        os.system(source_cmd)
        print(f"Sourced script: {script_file}")

    cleanup_cmd = f"ls -t /home/thahera/*_{timestamp}.sql | tail -n +4 | xargs rm -f"
    os.system(cleanup_cmd)
    print("Cleaned up older backups, keeping the latest 4.")

    print("Database operations completed.")
EOPYTHON

                        EOF
                    """
                }
            }
        }
    }
}
