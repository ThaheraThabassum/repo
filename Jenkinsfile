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
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
                    """
                }
            }
        }

        stage('Generate SQL Dump Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} <<'EOF'

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

df = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
script_list = []

for _, row in df.iterrows():
    db_name, table_name, option = row['database'], row['table'], str(row['option']).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()
    dump_file = f"{table_name}_{timestamp}.sql"
    
    dump_cmd = None
    if option == "data":
        dump_cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db_name} {table_name}"
    elif option == "structure":
        dump_cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db_name} {table_name}"
    elif option == "both":
        dump_cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name}"
    
    if dump_cmd:
        if where_condition.lower() != "nan":
            dump_cmd += f' --where="{where_condition}"'
        dump_cmd += f" > /home/thahera/{dump_file}"
        os.system(dump_cmd)
        script_list.append(dump_file)

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\n".join(script_list))
EOPYTHON
                        EOF
                    """
                }
            }
        }

        stage('Transfer Scripts') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/
                    """
                }
            }
        }

        stage('Backup, Drop, Delete & Load Data') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<'EOF'

                        python3 <<EOPYTHON
import pandas as pd
import os
import datetime

df = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    script_files = [line.strip() for line in f.readlines()]

for _, row in df.iterrows():
    db_name, table_name, option = row['database'], row['table'], str(row['option']).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    check_cmd = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -N -e 'SELECT COUNT(*) FROM information_schema.tables WHERE table_schema="{db_name}" AND table_name="{table_name}";'"
    table_exists = os.popen(check_cmd).read().strip()

    if table_exists == "1":
        backup_table = f"{table_name}_backup_{timestamp}"
        os.system(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE {db_name}.{backup_table} AS SELECT * FROM {db_name}.{table_name};"')
        
        if option == "structure":
            os.system(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{table_name};"')
        elif where_condition and where_condition.lower() != "nan":
            os.system(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DELETE FROM {db_name}.{table_name} WHERE {where_condition};"')

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}")
        script_files.remove(script_file)

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\n".join(script_files))
EOPYTHON
                        EOF
                    """
                }
            }
        }
    }
}
