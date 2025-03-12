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
                    sh '''
                        echo "Uploading Excel file to remote server..."
                        scp -o StrictHostKeyChecking=no "$WORKSPACE/$LOCAL_EXCEL_FILE" "$REMOTE_USER@$DEST_HOST:$REMOTE_EXCEL_PATH"
                    '''
                }
            }
        }

        stage('Generate SQL Dump Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Connecting to $REMOTE_HOST to generate scripts..."
                        ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST" << 'EOF'

                        echo "Successfully logged in!"
                        cd /home/thahera/
                        
                        echo "$SUDO_PASSWORD" | sudo -S apt install python3-pandas python3-openpyxl -y

                        python3 << 'EOPYTHON'
import pandas as pd
import os
import datetime

excel_file = "$REMOTE_EXCEL_PATH"
df = pd.read_excel(excel_file)

MYSQL_USER = "root"
MYSQL_PASSWORD = "AlgoTeam123"

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

for index, row in df.iterrows():
    db_name = row.get("database", "").strip()
    table_name = row.get("table", "").strip()
    option = str(row.get("option", "")).strip().lower()
    where_condition = str(row.get("where_condition", "")).strip()

    if not db_name or not table_name:
        print(f"Skipping row {index}: Missing database or table name")
        continue

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

                        exit
EOF
                    '''
                }
            }
        }

        stage('Transfer and Set Permissions') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Transferring generated scripts to $DEST_HOST..."
                        scp -o StrictHostKeyChecking=no "$REMOTE_USER@$REMOTE_HOST:/home/thahera/*.sql" "$REMOTE_USER@$DEST_HOST:/home/thahera/"

                        echo "Setting permissions for transferred files..."
                        ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$DEST_HOST" 'echo "$SUDO_PASSWORD" | sudo -S chmod 777 /home/thahera/*.sql'
                    '''
                }
            }
        }

        stage('Deploy SQL Scripts') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Deploying SQL scripts on $DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no "$REMOTE_USER@$DEST_HOST" << 'EOF'
                        echo "Successfully logged in!"
                        cd /home/thahera/

                        for sql_file in *.sql; do
                            if [ ! -f "$sql_file" ]; then
                                echo "Error: SQL file $sql_file not found!"
                                continue
                            fi

                            echo "Processing SQL file: $sql_file"

                            table_name=$(basename "$sql_file" | awk -F'_' '{print $1}')
                            timestamp=$(basename "$sql_file" | awk -F'_' '{print $2"_"$3"_"$4"_"$5"_"$6}')

                            db_name=$(grep -oP '(?<=USE `).*(?=`);' "$sql_file" | head -n 1)
                            if [ -z "$db_name" ]; then
                                echo "Database name could not be extracted from $sql_file, skipping..."
                                continue
                            fi

                            echo "Extracted Database: $db_name, Table: $table_name, File: $sql_file"

                            mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "USE $db_name"
                            
                            if mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "SHOW TABLES LIKE '$table_name'" | grep -q "$table_name"; then
                                backup_table="${table_name}_${timestamp}"
                                mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -e "CREATE TABLE $backup_table AS SELECT * FROM $table_name"

                                if [ $? -eq 0 ]; then
                                    echo "Backup created: $backup_table"
                                    mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < "$sql_file"
                                    echo "Script executed: $sql_file"
                                else
                                    echo "Backup creation failed for $table_name"
                                fi
                            else
                                echo "Table $table_name not found, executing script anyway..."
                                mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" < "$sql_file"
                            fi
                        done
                        exit
EOF
                    '''
                }
            }
        }
    }
}
