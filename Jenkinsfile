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
                sh 'git checkout kotak_db'
            }
        }

        stage('Pull Latest Changes') {
            steps {
                sh """
                    git reset --hard
                    git clean -fd
                    git pull origin kotak_db
                """
            }
        }

        stage('Upload Excel to Remote Servers') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        scp -o StrictHostKeyChecking=no ${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_EXCEL_PATH}
                        scp -o StrictHostKeyChecking=no ${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
                    """
                }
            }
        }

        stage('Generate SQL Scripts (No Backup)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
                            set -e
                            sudo apt install -y python3-pandas python3-openpyxl

                            python3 << EOPYTHON
import pandas as pd
import datetime
import subprocess

df = pd.read_excel("${REMOTE_EXCEL_PATH}")
MYSQL_USER = "${MYSQL_USER}"
MYSQL_PASSWORD = "${MYSQL_PASSWORD}"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
script_list = []

for _, row in df.iterrows():
    db = str(row["database"]).strip()
    table = str(row["table"]).strip()
    option = str(row["option"]).strip().lower()
    where = str(row.get("where_condition", "")).strip()

    check_db = f"mysql -u {MYSQL_USER} -p\\\"{MYSQL_PASSWORD}\\\" -N -e \\\"SHOW DATABASES LIKE '{db}'\\\""
    db_exists = subprocess.run(check_db, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    if not db_exists:
        print(f"❌ Skipping - DB not found: {db}")
        continue

    check_table = f"mysql -u {MYSQL_USER} -p\\\"{MYSQL_PASSWORD}\\\" -N -e \\\"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db}' AND table_name='{table}'\\\""
    table_exists = subprocess.run(check_table, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    if table_exists != '1':
        print(f"❌ Skipping - Table not found: {db}.{table}")
        continue

    dump_file = f"{table}_{timestamp}.sql"
    cmd = ""
    if option == "data":
        cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db} {table}"
        if where and where.lower() != "nan":
            cmd += f' --where="{where}"'
    elif option == "structure":
        cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db} {table}"
    elif option == "both":
        cmd = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db} {table}"
    
    if cmd:
        cmd += f" > /home/thahera/{dump_file}"
        try:
            subprocess.run(cmd, shell=True, check=True)
            script_list.append(dump_file)
            print(f"✅ Script generated: {dump_file}")
        except subprocess.CalledProcessError:
            print(f"❌ Error generating: {dump_file}")

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_list))
print("✅ All scripts written.")

EOPYTHON
EOF
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/*.sql ${REMOTE_USER}@${DEST_HOST}:/home/thahera/
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:${TRANSFERRED_SCRIPTS} ${REMOTE_USER}@${DEST_HOST}:${TRANSFERRED_SCRIPTS}
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'echo "${SUDO_PASSWORD}" | sudo -S chmod 777 /home/thahera/*.sql'
                    """
                }
            }
        }

        stage('Backup, Revert, Deploy in UAT') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} << 'EOF'
                            set -e

                            python3 << EOPYTHON
# === UAT Deployment Logic Starts ===
import pandas as pd
import datetime
import subprocess

MYSQL_USER = "${MYSQL_USER}"
MYSQL_PASSWORD = "${MYSQL_PASSWORD}"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

df = pd.read_excel("${REMOTE_EXCEL_PATH}")
with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    scripts = [line.strip() for line in f.readlines()]

for _, row in df.iterrows():
    db = str(row["database"]).strip()
    table = str(row["table"]).strip()
    option = str(row.get("option", "")).strip().lower()
    where = str(row.get("where_condition", "")).strip()
    cols_add = str(row.get("columns_need_to_add", "")).strip()
    dt_mod = str(row.get("change_the_datatype_for_columns", "")).strip()
    revert = str(row.get("revert", "")).strip().lower()

    def mysql(cmd):
        return subprocess.run(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{cmd}"', shell=True)

    if revert == "yes":
        renamed = f"{table}_rev_{timestamp}"
        mysql(f"RENAME TABLE {db}.{table} TO {db}.{renamed}")
        print(f"🔄 Reverted {table} -> {renamed}")
        try:
            get_latest = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db}' AND table_name LIKE '{table}_%' AND table_name NOT LIKE '%_rev_%' ORDER BY table_name DESC LIMIT 1;"
            latest = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{get_latest}"', shell=True).decode().strip()
            if latest:
                mysql(f"RENAME TABLE {db}.{latest} TO {db}.{table}")
                print(f"✅ Restored backup {latest} -> {table}")
        except:
            print(f"⚠️ No backup found to revert for {table}")
        continue

    check_exists = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=\'{db}\' AND table_name=\'{table}\'"', shell=True).decode().strip()
    if check_exists == "1":
        backup = f"{table}_{timestamp}"
        mysql(f"CREATE TABLE {db}.{backup} LIKE {db}.{table}")
        mysql(f"INSERT INTO {db}.{backup} SELECT * FROM {db}.{table}")
        print(f"✅ Backup created: {backup}")

    changes_made = False

    if cols_add and cols_add.lower() != "nan":
        for col in cols_add.split(","):
            colname = col.strip().split()[0]
            colcheck = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}' AND column_name='{colname}'"
            exists = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{colcheck}"', shell=True).decode().strip()
            if exists == '0':
                mysql(f"ALTER TABLE {db}.{table} ADD COLUMN {col.strip()}")
                print(f"➕ Column added: {col.strip()}")
                changes_made = True

    if dt_mod and dt_mod.lower() != "nan":
        for mod in dt_mod.split(","):
            col = mod.strip().split()[0]
            check = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}' AND column_name='{col}'"
            exists = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check}"', shell=True).decode().strip()
            if exists == '1':
                mysql(f"ALTER TABLE {db}.{table} MODIFY COLUMN {mod.strip()}")
                print(f"🛠 Column modified: {mod.strip()}")
                changes_made = True

    if option == "data":
        del_q = f"DELETE FROM {db}.{table}" if not where or where.lower() == "nan" else f"DELETE FROM {db}.{table} WHERE {where}"
        mysql(del_q)

    elif option == "structure":
        mysql(f"DROP TABLE {db}.{table}")

    script_file = next((s for s in scripts if s.startswith(table)), None)
    if script_file:
        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" {db} < /home/thahera/{script_file}', shell=True)
        print(f"✅ Loaded script: {script_file}")
        changes_made = True

    # Cleanup old backups and _rev_ if changes happened
    if changes_made:
        cleanup = f'''
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='{db}' 
            AND table_name LIKE '{table}_%' 
            AND table_name NOT LIKE '%_rev_%' 
            ORDER BY table_name DESC LIMIT 3, 100;
        '''
        backups = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{cleanup}"', shell=True).decode().strip().split("\\n")
        for b in backups:
            if b:
                mysql(f"DROP TABLE {db}.{b}")
                print(f"🗑 Dropped old backup: {b}")

        get_old = f'''
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='{db}' 
            AND table_name LIKE '{table}_%' 
            AND table_name NOT LIKE '%_rev_%'
            ORDER BY table_name ASC LIMIT 1;
        '''
        old_base = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{get_old}"', shell=True).decode().strip()
        revs = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "SELECT table_name FROM information_schema.tables WHERE table_schema='{db}' AND table_name LIKE '{table}_rev_%'"', shell=True).decode().strip().split("\\n")
        for rev in revs:
            if rev.replace(f"{table}_rev_", "") < old_base.replace(f"{table}_", ""):
                mysql(f"DROP TABLE {db}.{rev}")
                print(f"🗑 Dropped _rev_ backup: {rev}")

# === UAT Deployment Logic Ends ===
EOPYTHON
EOF
                    """
                }
            }
        }
    }
}
