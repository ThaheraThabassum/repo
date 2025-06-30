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
                sh '''
                    git reset --hard
                    git clean -fd
                    git pull origin kotak_db
                '''
            }
        }

        stage('Upload Excel to Remote Servers') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        scp -o StrictHostKeyChecking=no ${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_EXCEL_PATH}
                        scp -o StrictHostKeyChecking=no ${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
                    '''
                }
            }
        }

        #stage('Generate SQL Scripts (No Backup)') {
            #steps {
                #sshagent(credentials: [SSH_KEY]) {
                    #sh """
                        #ssh -tt -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << EOF
                            #set -e
                            #echo "${SUDO_PASSWORD}" | sudo -S apt install -y python3-pandas python3-openpyxl
        stage('Generate SQL Scripts (No Backup)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} 'bash -s' << 'EOF'
set -e
echo "${SUDO_PASSWORD}" | sudo -S apt install -y python3-pandas python3-openpyxl

                            python3 << EOPYTHON
import pandas as pd
import datetime
import subprocess

MYSQL_USER = "${MYSQL_USER}"
MYSQL_PASSWORD = "${MYSQL_PASSWORD}"
df = pd.read_excel("${REMOTE_EXCEL_PATH}")
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
script_list = []

for _, row in df.iterrows():
    db = str(row["database"]).strip()
    table = str(row["table"]).strip()
    option = str(row["option"]).strip().lower()
    where = str(row.get("where_condition", "")).strip()

    #check_db = f"mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SHOW DATABASES LIKE '{db}'\""
    check_db = f"mysql -u {MYSQL_USER} -p\\\"{MYSQL_PASSWORD}\\\" -N -e \\\"SHOW DATABASES LIKE '{db}'\\\""
    db_exists = subprocess.run(check_db, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    if not db_exists:
        print(f"❌ Skipping - DB not found: {db}")
        continue

    #check_table = f"mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db}' AND table_name='{table}'\""
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

TRANSFERRED_SCRIPTS = "/home/thahera/transferred_scripts.txt"
with open(TRANSFERRED_SCRIPTS, "w") as f:
    f.write("\\n".join(script_list))
print("✅ All scripts written.")
EOPYTHON
EOF
                    """
                }
            }
        }

        stage('Transfer Scripts to DEST_HOST') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "📥 Fetching transferred_scripts.txt from REMOTE_HOST to local..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "cat ${TRANSFERRED_SCRIPTS}" > transferred_scripts.txt

                        echo "📤 Sending transferred_scripts.txt to DEST_HOST..."
                        scp -o StrictHostKeyChecking=no transferred_scripts.txt ${REMOTE_USER}@${DEST_HOST}:${TRANSFERRED_SCRIPTS}

                        echo "📦 Transferring scripts listed in transferred_scripts.txt..."
                        while read script; do
                            echo "🔁 Transferring \$script..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "[ -f /home/thahera/\$script ]" && \\
                            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST}:/home/thahera/\$script ${REMOTE_USER}@${DEST_HOST}:/home/thahera/ || \\
                            echo "⚠️ Skipped \$script (not found on REMOTE_HOST)"
                        done < transferred_scripts.txt

                        echo "🔐 Setting file permissions on DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "echo '${SUDO_PASSWORD}' | sudo -S chmod 777 /home/thahera/*.sql"
                    '''
                }
            }
        }



        stage('Backup, Revert, Deploy in UAT') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} << 'EOF'
                            set -e
                            python3 << EOPYTHON
import pandas as pd
import datetime
import subprocess

MYSQL_USER = "${MYSQL_USER}"
MYSQL_PASSWORD = "${MYSQL_PASSWORD}"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
df = pd.read_excel("${REMOTE_EXCEL_PATH}")
with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    scripts = [line.strip() for line in f.readlines()]

def mysql(cmd):
    return subprocess.run(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{cmd}"', shell=True)

for _, row in df.iterrows():
    try:
        db = str(row["database"]).strip()
        table = str(row["table"]).strip()
        option = str(row.get("option", "")).strip().lower()
        where = str(row.get("where_condition", "")).strip()
        cols_add = str(row.get("columns_need_to_add", "")).strip()
        dt_mod = str(row.get("change_the_datatype_for_columns", "")).strip()
        revert = str(row.get("revert", "")).strip().lower()

        if revert == "yes":
            renamed = f"{table}_rev_{timestamp}"
            mysql(f"RENAME TABLE {db}.{table} TO {db}.{renamed}")
            get_latest = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db}' AND table_name LIKE '{table}_%' AND table_name NOT LIKE '%_rev_%' ORDER BY table_name DESC LIMIT 1;"
            latest = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{get_latest}"', shell=True).decode().strip()
            if latest:
                mysql(f"RENAME TABLE {db}.{latest} TO {db}.{table}")
            continue

        should_skip_backup = True
        if option and option != "nan":
            should_skip_backup = False
        if cols_add and cols_add.lower() != "nan":
            for col in cols_add.split(","):
                colname = col.strip().split()[0]
                check = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}' AND column_name='{colname}'"
                exists = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check}"', shell=True).decode().strip()
                if exists == '0':
                    should_skip_backup = False
                    break
        if dt_mod and dt_mod.lower() != "nan":
            for mod in dt_mod.split(","):
                col = mod.strip().split()[0]
                check = f"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db}' AND table_name='{table}' AND column_name='{col}'"
                exists = subprocess.check_output(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check}"', shell=True).decode().strip()
                if exists == '1':
                    should_skip_backup = False
                    break

        if not should_skip_backup:
            backup = f"{table}_{timestamp}"
            mysql(f"CREATE TABLE {db}.{backup} LIKE {db}.{table}")
            mysql(f"INSERT INTO {db}.{backup} SELECT * FROM {db}.{table}")

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

        if changes_made:
            cleanup_query = f"""
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='{db}' 
            AND table_name LIKE '{table}_%' 
            AND table_name NOT LIKE '%_rev_%' 
            ORDER BY table_name DESC LIMIT 3, 100;
            """
            cleanup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{cleanup_query}"'
            try:
                old_backups = subprocess.check_output(cleanup_command, shell=True).decode().strip().split("\n")
                for backup in old_backups:
                    if backup:
                        delete_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db}.{backup};"'
                        subprocess.call(delete_backup, shell=True)
                        print(f"🗑 Deleted old backup: {backup}")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ No old backups found or error occurred: {e}")

            get_oldest_backup_query = f"""
                SELECT table_name FROM information_schema.tables 
                WHERE table_schema='{db}' 
                AND table_name LIKE '{table}_%' 
                AND table_name NOT LIKE '%_rev_%' 
                ORDER BY table_name ASC LIMIT 1;
            """
            oldest_backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{get_oldest_backup_query}"'
            try:
                oldest_backup = subprocess.check_output(oldest_backup_command, shell=True).decode().strip()
                if oldest_backup:
                    print(f"🔎 Oldest retained backup: {oldest_backup}")

                    rev_backup_query = f"""
                        SELECT table_name FROM information_schema.tables 
                        WHERE table_schema='{db}' 
                        AND table_name LIKE '{table}_rev_%';
                    """
                    rev_backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{rev_backup_query}"'
                    rev_backups = subprocess.check_output(rev_backup_command, shell=True).decode().strip().split("\n")

                    for rev_backup in rev_backups:
                        if rev_backup:
                            normal_time = oldest_backup.replace(table + "_", "")
                            rev_time = rev_backup.replace(table + "_rev_", "")
                            if rev_time < normal_time:
                                delete_rev_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db}.{rev_backup};"'
                                subprocess.call(delete_rev_backup, shell=True)
                                print(f"🗑 Deleted old _rev_ backup: {rev_backup}")
                else:
                    print(f"⚠️ No normal backups found for {table}, skipping _rev_ backup cleanup.")
            except subprocess.CalledProcessError as e:
                print(f"❌ Error fetching oldest backup: {e}")

    except Exception as e:
        print(f"⚠️ Error while processing row: {e}")
        continue
EOPYTHON
EOF
                    '''
                }
            }
        }
    }
}
