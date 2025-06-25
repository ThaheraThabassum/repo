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
                    sh 'git checkout kotak_db'
                }
            }
        }

        stage('Pull Latest Changes') {
            steps {
                script {
                    echo "Pulling latest changes from Git..."
                    sh """
                        git reset --hard
                        git clean -fd
                        git pull origin kotak_db  # Change 'main' if using a different branch
                    """
                }
            }
        }    
        stage('Upload Excel to Remote Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Uploading Excel file to remote server..."
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_EXCEL_PATH}
                        scp -o StrictHostKeyChecking=no ${WORKSPACE}/${LOCAL_EXCEL_FILE} ${REMOTE_USER}@${DEST_HOST}:${REMOTE_EXCEL_PATH}
                        
                    """
                }
            }
        }

        stage('Generate and Transfer SQL Dump Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Generating SQL dump files on ${REMOTE_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << 'EOF'
                            set -e
                            echo "Successfully logged into ${REMOTE_HOST}"

                            cd /home/thahera/
                            echo '${SUDO_PASSWORD}' | sudo -S apt install -y python3-pandas python3-openpyxl

                            python3 << EOPYTHON
import pandas as pd
import datetime
import subprocess

excel_file = "${REMOTE_EXCEL_PATH}"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")
script_list = []

for _, row in df.iterrows():
    db_name = str(row["database"]).strip()
    table_name = str(row["table"]).strip()
    option = str(row["option"]).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()
    columns_to_add = str(row.get("columns_need_to_add", "")).strip()
    datatype_changes = str(row.get("change_the_datatype_for_columns", "")).strip()
    revert = str(row.get("revert", "")).strip().lower()

    # Validate DB
    check_db_cmd = f'mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SHOW DATABASES LIKE "{db_name}"\"'
    db_exists = subprocess.run(check_db_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    if not db_exists:
        print(f'\u274c Skipping - Database does not exist: {db_name}')
        continue
 
    # Validate Table
    #check_table_cmd = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=\'{db_name}\' AND table_name=\'{table_name}\'"'
    #check_table_cmd = f"mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}'\""
    check_table_cmd = f"""mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e 'SELECT COUNT(*) FROM information_schema.tables WHERE table_schema="{db_name}" AND table_name="{table_name}"'"""
    table_exists = subprocess.run(check_table_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
    if table_exists != '1':
        print(f'\u274c Skipping - Table does not exist: {db_name}.{table_name}')
        continue
 
    # Validate datatype modification columns
    if datatype_changes and datatype_changes.lower() != "nan":
        modify_list = [col.strip() for col in datatype_changes.split(",")]
        for mod in modify_list:
            column_name = mod.split()[0]
            #check_col_cmd = f'mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db_name}' AND table_name='{table_name}' AND column_name='{column_name}'\"'
            check_col_cmd = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=\'{db_name}\' AND table_name=\'{table_name}\' AND column_name=\'{column_name}\'"'
            col_exists = subprocess.run(check_col_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
            if col_exists != '1':
                print(f"\u274c Skipping - Column '{column_name}' doesn't exist in {db_name}.{table_name} for modification")
                continue
 
    # Validate column existence before ADD
    if columns_to_add and columns_to_add.lower() != "nan":
        column_defs = [col.strip() for col in columns_to_add.split(",")]
        for col_def in column_defs:
            col_name = col_def.split()[0]
            #check_col_cmd = f'mysql -u {MYSQL_USER} -p\"{MYSQL_PASSWORD}\" -N -e \"SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='{db_name}' AND table_name='{table_name}' AND column_name='{col_name}'\"'
            check_col_cmd = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema=\'{db_name}\' AND table_name=\'{table_name}\' AND column_name=\'{col_name}\'"'
            col_exists = subprocess.run(check_col_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
            if col_exists == '1':
                print(f"\u26a0\ufe0f Skipping column add - Column '{col_name}' already exists in {db_name}.{table_name}")
                continue:

    print(f'🔍 Processing: {db_name}.{table_name} | Option: {option} | Where: {where_condition} | columns_to_add: {columns_to_add } | datatype_changes: {datatype_changes} | revert: {revert}')  # Debug Print

    dump_file = f"{table_name}_{timestamp}.sql"
    dump_command = None

    if option == "data":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-create-info {db_name} {table_name}"
        if where_condition and where_condition.lower() != "nan":
            dump_command += f' --where="{where_condition}"'

    elif option == "structure":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' --no-data {db_name} {table_name}"

    elif option == "both":
        dump_command = f"mysqldump -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} {table_name}"

    if dump_command:
        dump_command += f" > /home/thahera/{dump_file}"
        try:
            subprocess.run(dump_command, shell=True, check=True, capture_output=True, text=True)
            print(f"✅ Dump generated: {dump_file}")
            script_list.append(dump_file)
        except subprocess.CalledProcessError as e:
            print(f"❌ Error executing dump: {e.stderr}")

with open("${TRANSFERRED_SCRIPTS}", "w") as f:
    f.write("\\n".join(script_list))

print("✅ Scripts generated successfully.")
print(f"🕒 Timestamp: {timestamp}")

EOPYTHON
EOF

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
import numpy as np

databases = pd.read_excel("${REMOTE_EXCEL_PATH}") # Corrected line

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

with open("${TRANSFERRED_SCRIPTS}", "r") as f:
    script_files = [line.strip() for line in f.readlines()]

for _, row in databases.iterrows():
    db_name = row["database"]
    table_name = row["table"]
    option = row["option"]
    if isinstance(option, str): #Check if its a String
        option = option.strip().lower() #Strip only if it is a string
    else:
        option = str(option).lower() #Convert to string and lower if not a string.
        if option == 'nan':
            option = '' #Set to empty string if its nan.
    where_condition = str(row.get("where_condition", "")).strip()
    columns_to_add = str(row.get("columns_need_to_add", "")).strip()
    datatype_changes = str(row.get("change_the_datatype_for_columns", "")).strip()
    revert = str(row.get("revert", "")).strip().lower()

    if revert == "yes":
        print(f"🔄 Reverting table: {table_name} in database: {db_name}")
        
        renamed_table = f"{table_name}_rev_{timestamp}"
        rename_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "RENAME TABLE {db_name}.{table_name} TO {db_name}.{renamed_table};"'
        subprocess.call(rename_command, shell=True)
        print(f"✅ Renamed {table_name} to {renamed_table}")
        
        find_backup_query = f"SELECT table_name FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name LIKE '{table_name}_%' AND table_name NOT LIKE '%_rev_%' ORDER BY table_name DESC LIMIT 1;"

        find_backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{find_backup_query}"'

        try:
            latest_backup = subprocess.check_output(find_backup_command, shell=True).decode().strip()
            if latest_backup:
                restore_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "RENAME TABLE {db_name}.{latest_backup} TO {db_name}.{table_name};"'
                subprocess.call(restore_command, shell=True)
                print(f"✅ Restored latest backup {latest_backup} as {table_name}")
            else:
                print(f"⚠️ No backups found for {table_name}, revert skipped.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error finding latest backup: {e}")
            continue
        continue
        
    check_query = f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='{db_name}' AND table_name='{table_name}';"
    check_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{check_query}"'

    try:
        result = subprocess.check_output(check_command, shell=True).decode().strip()
    except subprocess.CalledProcessError as e:
        print(f"❌ Error checking table: {e}")
        continue

    if result == "1":
        backup_table = f"{table_name}_{timestamp}"
        create_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "CREATE TABLE {db_name}.{backup_table} LIKE {db_name}.{table_name};"'
        backup_data = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "INSERT INTO {db_name}.{backup_table} SELECT * FROM {db_name}.{table_name};"'
        subprocess.call(create_backup, shell=True)
        subprocess.call(backup_data, shell=True)
        print(f"✅ Backup created: {backup_table}")

    changes_made = False 

    # Add new columns if specified
    if columns_to_add and columns_to_add.lower() != "nan":
        columns = [col.strip() for col in columns_to_add.split(",")]
        for column in columns:
            add_column_query = f'ALTER TABLE {db_name}.{table_name} ADD COLUMN {column};'
            add_column_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{add_column_query}"'
            result = subprocess.call(add_column_command, shell=True)

            if result == 0:
                print(f"✅ Column added: {column}")
                changes_made = True

    # Modify column data types if specified
    if datatype_changes and datatype_changes.lower() != "nan":
        datatype_changes_list = [change.strip() for change in datatype_changes.split(",")]
        for change in datatype_changes_list:
            modify_column_query = f'ALTER TABLE {db_name}.{table_name} MODIFY COLUMN {change};'
            modify_column_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{modify_column_query}"'
            result = subprocess.call(modify_column_command, shell=True)

            if result == 0:
                print(f"✅ Column datatype modified: {change}")
                changes_made = True
    
    if option == "data":
        delete_query = f"DELETE FROM {db_name}.{table_name}" if not where_condition or where_condition.lower() == "nan" else f"DELETE FROM {db_name}.{table_name} WHERE {where_condition}"
        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{delete_query}"', shell=True)

    elif option == "structure":
        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{table_name};"', shell=True)

    script_file = next((s for s in script_files if s.startswith(table_name)), None)
    if script_file:
        script_load_command = f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}"
        result = subprocess.call(script_load_command, shell=True)

        if result == 0:  # Check if script executed successfully
            print(f"✅ Successfully loaded script: {script_file}")
            changes_made = True
            
    if changes_made:
        # Delete old backups (excluding `_rev_` backups)
        cleanup_query = f'''
        SELECT table_name FROM information_schema.tables 
        WHERE table_schema='{db_name}' 
        AND table_name LIKE '{table_name}_%' 
        AND table_name NOT LIKE '%_rev_%'  -- Exclude _rev_ backups
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

        #compare 
        get_oldest_backup_query = f'''
            SELECT table_name FROM information_schema.tables 
            WHERE table_schema='{db_name}' 
            AND table_name LIKE '{table_name}_%' 
            AND table_name NOT LIKE '%_rev_%'
            ORDER BY table_name ASC LIMIT 1;
        '''
        oldest_backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{get_oldest_backup_query}"'
        try:
            oldest_backup = subprocess.check_output(oldest_backup_command, shell=True).decode().strip()
            if oldest_backup:
                print(f"🔎 Oldest retained backup: {oldest_backup}")

                # Find and delete old `_rev_` backups
                rev_backup_query = f'''
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema='{db_name}' 
                    AND table_name LIKE '{table_name}_rev_%';
                '''
                rev_backup_command = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -N -e "{rev_backup_query}"'
            
                rev_backups = subprocess.check_output(rev_backup_command, shell=True).decode().strip().split("\\n")
            
                for rev_backup in rev_backups:
                    if rev_backup:
                        # Extract timestamps from table names
                        normal_time = oldest_backup.replace(table_name + "_", "")
                        rev_time = rev_backup.replace(table_name + "_rev_", "")
                    
                        if rev_time < normal_time:
                            delete_rev_backup = f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{rev_backup};"'
                            subprocess.call(delete_rev_backup, shell=True)
                            print(f"🗑 Deleted old _rev_ backup: {rev_backup}")
            else:
                print(f"⚠️ No normal backups found for {table_name}, skipping _rev_ backup cleanup.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Error fetching oldest backup: {e}")
       
        
EOPYTHON
EOF
                    """
                }
            }
        }
    }
}
