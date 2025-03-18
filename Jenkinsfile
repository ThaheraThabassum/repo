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

        stage('Clean Workspace') {

            steps {

                cleanWs()  // Clean Jenkins workspace to avoid stale data

            }

        }
 
        stage('Checkout Main Branch') {

            steps {

                script {

                    echo "Checking out main branch..."

                    sh 'git checkout main'

                }

            }

        }
 
        stage('Clean Previous Excel on Remote Servers') {

            steps {

                sshagent(credentials: [SSH_KEY]) {

                    sh """

                        echo "Cleaning old Excel file on remote servers..."

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} 'rm -f ${REMOTE_EXCEL_PATH}'

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} 'rm -f ${REMOTE_EXCEL_PATH}'

                    """

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
 
        stage('Verify Uploaded Excel') {

            steps {

                sshagent(credentials: [SSH_KEY]) {

                    sh """

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "ls -l ${REMOTE_EXCEL_PATH}"

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cat ${REMOTE_EXCEL_PATH}"

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
 
                            # Kill stale Python processes to avoid cached data

                            pkill -f python || true  
 
                            cd /home/thahera/

                            echo '${SUDO_PASSWORD}' | sudo -S apt install -y python3-pandas python3-openpyxl
 
                            echo "🔍 Debug: Checking Excel File Content"

                            python3 -c "import pandas as pd; df = pd.read_excel('${REMOTE_EXCEL_PATH}', engine='openpyxl'); print(df)"
 
                            python3 << EOPYTHON

import pandas as pd

import datetime

import subprocess

import os

import time
 
excel_file = "${REMOTE_EXCEL_PATH}"
 
# Refresh file metadata to ensure latest data is read

if os.path.exists(excel_file):

    os.utime(excel_file, None)

    time.sleep(2)
 
df = pd.read_excel(excel_file, engine='openpyxl')
 
MYSQL_USER = "root"

MYSQL_PASSWORD = "AlgoTeam123"
 
timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

script_list = []
 
for _, row in df.iterrows():

    db_name = str(row["database"]).strip()

    table_name = str(row["table"]).strip()

    option = str(row["option"]).strip().lower()

    where_condition = str(row.get("where_condition", "")).strip()
 
    print(f"🔍 Processing: {db_name}.{table_name} | Option: {option} | Where: {where_condition}")  
 
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

                            pkill -f python || true  
 
                            python3 << EOPYTHON

import pandas as pd

import datetime

import subprocess
 
databases = pd.read_excel("${REMOTE_EXCEL_PATH}", engine='openpyxl')
 
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
 
    if option == "data":

        delete_query = f"DELETE FROM {db_name}.{table_name}" if not where_condition else f"DELETE FROM {db_name}.{table_name} WHERE {where_condition}"

        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "{delete_query}"', shell=True)
 
    elif option == "structure":

        subprocess.call(f'mysql -u {MYSQL_USER} -p"{MYSQL_PASSWORD}" -e "DROP TABLE {db_name}.{table_name};"', shell=True)
 
    script_file = next((s for s in script_files if s.startswith(table_name)), None)

    if script_file:

        subprocess.call(f"mysql -u {MYSQL_USER} -p'{MYSQL_PASSWORD}' {db_name} < /home/thahera/{script_file}", shell=True)

        print(f"✅ Loaded script: {script_file}")

EOPYTHON

EOF

                    """

                }

            }

        }

    }

}

 
