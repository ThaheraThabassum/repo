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

databases = pd.read_excel("${REMOTE_EXCEL_PATH}")

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

script_list = []

for index, row in databases.iterrows():
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
        script_list.append(dump_file)

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_list))

EOPYTHON
                        EOF
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
    check_command = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' -N -e '{check_query}'"
    table_exists = os.popen(check_command).read().strip()

    if table_exists == "1":
        print(f"✅ Table '{table_name}' exists in '{db_name}', taking backup...")
        backup_table = f"{table_name}_backup_{timestamp}"

        backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE {db_name}.{backup_table} LIKE {db_name}.{table_name}; INSERT INTO {db_name}.{backup_table} SELECT * FROM {db_name}.{table_name};"'
        backup_status = os.system(backup_command)

        if backup_status == 0:
            print(f"✅ Backup created: {backup_table}")
        else:
            print(f"❌ Backup failed for {table_name} in {db_name}")

        if option == "structure":
            os.system(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{table_name};"')
            print(f"⚠️ Table '{table_name}' dropped.")

        elif where_condition and where_condition.lower() != "nan":
            where_condition = where_condition.strip()
            if " " not in where_condition or "=" not in where_condition:
                print(f"⚠️ Invalid where_condition '{where_condition}', skipping delete.")
            else:
                os.system(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DELETE FROM {db_name}.{table_name} WHERE {where_condition};"')
                print(f"⚠️ Deleted data from {table_name} where {where_condition}")

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        os.system(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}")
        print(f"✅ Sourced script: {script_file}")
        script_files.remove(script_file)

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_files))

EOPYTHON
                        EOF
                    """
                }
            }
        }
    }
}
