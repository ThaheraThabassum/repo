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
        stage('Checkout Main Branch') {
            steps {
                script {
                    echo "Checking out main branch..."
                    sh 'git checkout main'
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
                        echo "Processing tables on ${DEST_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} << 'EOF'
                            set -e

                            python3 << EOPYTHON
import pandas as pd
import datetime
import subprocess

databases = pd.read_excel("${REMOTE_EXCEL_PATH}")

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    script_files = [line.strip() for line in f.readlines()]

for _, row in databases.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = row["option"].strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    check_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}';"
    check_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check_query}"'

    try:
        result = subprocess.check_output(check_command, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking table: {e}")
        continue

    if result == "1":
        # Backup creation
        backup_table = f"{table_name}_{timestamp}"
        create_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE {db_name}.{backup_table} LIKE {db_name}.{table_name};"'
        backup_data = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "INSERT INTO {db_name}.{backup_table} SELECT * FROM {db_name}.{table_name};"'
        subprocess.call(create_backup, shell=True)
        subprocess.call(backup_data, shell=True)
        print(f"✅ Backup created: {backup_table}")

        # Delete older backups (keep only last 3)
        cleanup_query = f'''
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='{db_name}' 
        AND table_name LIKE '{table_name}_%' 
        ORDER BY table_name DESC LIMIT 3, 100;
        '''
        cleanup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{cleanup_query}"'
        
        try:
            old_backups = subprocess.check_output(cleanup_command, shell=True).decode().strip().split("\\n")
            for backup in old_backups:
                if backup:
                    delete_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{backup};"'
                    subprocess.call(delete_backup, shell=True)
                    print(f"🗑 Deleted old backup: {backup}")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ No old backups found or error occurred: {e}")

    if option == "data":
        delete_query = f"DELETE FROM {db_name}.{table_name}" if not where_condition else f"DELETE FROM {db_name}.{table_name} WHERE {where_condition}"
        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{delete_query}"', shell=True)

    elif option == "structure":
        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{table_name};"', shell=True)

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        subprocess.call(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}", shell=True)

EOPYTHON
EOF
                    """
                }
            }
        }
    }
}
