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
import subprocess

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
script_list = []

for index, row in df.iterrows():
    db_name = str(row["database"]).strip()
    table_name = str(row["table"]).strip()
    option = str(row["option"]).strip().lower()  # Ensure it's lowercase and trimmed
    where_condition = str(row.get("where_condition", "")).strip()

    print(f"🔍 Processing: {db_name}.{table_name} | Option: {option} | Where: {where_condition}")  # Debug Print

    dump_file = f"{table_name}_{timestamp}.sql"
    dump_command = None

    if option == "data":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db_name} {table_name}"
        if where_condition and where_condition.lower() != "nan":
            where_condition = where_condition.replace('"', '\\"')  # Escape double quotes
            dump_command += f' --where="{where_condition}"'

    elif option == "structure":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db_name} {table_name}"

    elif option == "both":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name}"

    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        
        print(f"🟢 Running Command: {dump_command}")  # DEBUG PRINT

        try:
            result = subprocess.run(dump_command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ Dump generated: {dump_file}")
            script_list.append(dump_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing dump: {e.stderr}")

# Save transferred scripts list
with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_list))

print("✅ Scripts generated successfully in /home/thahera/")
print(f"🕒 Timestamp used: {timestamp}")

EOPYTHON

                        logout
                        EOF
                    """
                }
            }
        }

        stage('Transfer and Store Script Names') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Transferring generated scripts to ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} 'cat ${TRANSFERRED_SCRIPTS}' > transferred_scripts.txt
                        scp -o StrictHostKeyChecking=no transferred_scripts.txt ${REMOTE_USER}@${DEST_HOST}:${TRANSFERRED_SCRIPTS}

                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/

                        echo "Setting permissions for transferred files..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'echo "${SUDO_PASSWORD}" | sudo -S chmod 777 /home/thahera/*.sql'
                    """
                }
            }
        }

        stage('Backup, Drop, Delete & Load Data') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Processing tables for backup, deletion, and data loading on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime
import subprocess

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
    
    try:
        result = subprocess.check_output(check_command, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking table existence: {e}")
        continue

    if result == "1":
        print(f"✅ Table '{table_name}' exists in '{db_name}', taking backup...")
        backup_table = f"{table_name}_{timestamp}"

        create_backup_structure = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE IF NOT EXISTS {db_name}.{backup_table} LIKE {db_name}.{table_name};"'
        backup_data_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "INSERT INTO {db_name}.{backup_table} SELECT * FROM {db_name}.{table_name};"'
        
        try:
            subprocess.check_call(create_backup_structure, shell=True)
            subprocess.check_call(backup_data_command, shell=True)
            print(f"✅ Backup created: {backup_table}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error creating backup table: {e}")
            continue

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        subprocess.call(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}", shell=True)
        print(f"✅ Loaded script: {script_file}")

EOPYTHON

                        logout
                        EOF
                    """
                }
            }
        }
    }
}
