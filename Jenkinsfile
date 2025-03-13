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

        stage('Process Database Operations') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Processing databases on ${DEST_HOST} based on db_config.xlsx..."
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

for index, row in df.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    where_condition = str(row.get("where_condition", "")).strip()

    backup_table = f"{table_name}_backup_{datetime.datetime.now().strftime('%d_%m_%y_%H_%M_%S')}"
    os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; CREATE TABLE {backup_table} AS SELECT * FROM {table_name};'")
    print(f"Backup created: {backup_table}")

    if where_condition and where_condition.lower() != "nan":
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -e 'USE {db_name}; DELETE FROM {table_name} WHERE {where_condition};'")
        print(f"Deleted data from {table_name} where {where_condition}")

    sql_files = sorted([f for f in os.listdir("/home/thahera") if f.startswith(table_name) and f.endswith(".sql")], key=os.path.getmtime, reverse=True)
    if sql_files:
        latest_sql_file = sql_files[0]
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{latest_sql_file}")
        print(f"Sourced latest script: {latest_sql_file}")

    if len(sql_files) > 4:
        for old_file in sql_files[4:]:
            os.remove(f"/home/thahera/{old_file}")
            print(f"Deleted old backup: {old_file}")

print("Database operations completed.")
EOPYTHON
                        EOF
                    """
                }
            }
        }
    }
}
