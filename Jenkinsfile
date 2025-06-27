pipeline {
    agent any

    environment {
        FILES_LIST_FILE = "files_to_revert.txt"
        REMOTE_USER = "thahera"
        REMOTE_HOST = "65.1.176.9"
        BASE_PATH = "/home/ubuntu/ACE-Camunda-DevOps"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
    }

    stages {
        stage('Revert Files/Folders Directly on Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "📂 Reading files to revert from ${FILES_LIST_FILE}..."
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r FILE_PATH || [[ -n "$FILE_PATH" ]]; do
                            FILE_PATH=$(echo "$FILE_PATH" | xargs)  # Trim whitespace
                            [ -z "$FILE_PATH" ] && continue

                            echo "========== Reverting: $FILE_PATH =========="

                            DEST_PATH="${BASE_PATH}/$FILE_PATH"
                            FILE_NAME=$(basename "$FILE_PATH")
                            DEST_DIR=$(dirname "$DEST_PATH")

                            echo "🔎 Checking existence on DEST_HOST..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "bash -c '
                                if [ -e \"$DEST_PATH\" ]; then
                                    echo \"📦 Backing up: \$DEST_PATH -> \${DEST_PATH}_rev_${TIMESTAMP}\"
                                    sudo cp -r \"\$DEST_PATH\" \"\${DEST_PATH}_rev_${TIMESTAMP}\"
                                else
                                    echo \"❌ \$DEST_PATH does not exist, skipping backup.\"
                                fi
                            '"

                            echo "🔁 Attempting restore from previous backup..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "bash -c '
                                cd \"$DEST_DIR\"
                                LATEST=\$(ls -td ${FILE_NAME}_* 2>/dev/null | grep -v _rev_ | head -n 1)

                                if [ -n \"\$LATEST\" ] && [ -e \"\$LATEST\" ]; then
                                    echo \"✅ Restoring backup: \$LATEST -> \$DEST_PATH\"
                                    sudo rm -rf \"\$DEST_PATH\"
                                    sudo cp -r \"\$LATEST\" \"\$DEST_PATH\"
                                else
                                    echo \"⚠️ No valid backup found to restore.\"
                                fi

                                echo \"🧹 Cleaning up old _rev_ backups...\"
                                ls -dt ${FILE_NAME}_rev_* 2>/dev/null | tail -n +3 | xargs -r sudo rm -rf
                            '"

                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Restart Docker on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "==============================="
                        echo "🔄 Restarting Docker containers on DEST_HOST"
                        echo "==============================="

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c '
                            cd ${BASE_PATH}
                            #sudo docker-compose down
                            #sudo docker-compose up --build -d --force-recreate
                        '
                    '''
                }
            }
        }
    }
}
