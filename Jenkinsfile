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
                        echo "Reading files to revert from ${FILES_LIST_FILE}..."
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r FILE_PATH; do
                            FILE_PATH=$(echo "$FILE_PATH" | xargs)  # Trim whitespace
                            [ -z "$FILE_PATH" ] && continue

                            echo "========== Reverting: $FILE_PATH =========="

                            DEST_PATH="${BASE_PATH}/$FILE_PATH"
                            FILE_NAME=$(basename "$FILE_PATH")
                            DEST_DIR=$(dirname "$DEST_PATH")

                            # Backup current file/folder as _rev_ if it exists
                            echo "🔎 Checking existence on DEST_HOST..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                                if [ -e \"$DEST_PATH\" ]; then
                                    echo \"📦 Backing up existing item: $DEST_PATH -> ${DEST_PATH}_rev_${TIMESTAMP}\"
                                    cp -r \"$DEST_PATH\" \"${DEST_PATH}_rev_${TIMESTAMP}\"
                                else
                                    echo \"❌ $DEST_PATH does not exist, skipping backup.\"
                                fi
                            '"

                            # Try to restore from latest *_timestamp backup (excluding _rev_)
                            echo "🔁 Attempting restore from previous backup..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                                cd \"$DEST_DIR\"

                                LATEST=\$(ls -td ${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | head -n1 || true)

                                if [ -n \"$LATEST\" ] && [ -e \"$LATEST\" ]; then
                                    echo \"✅ Restoring backup: \$LATEST -> $DEST_PATH\"
                                    rm -rf \"$DEST_PATH\"
                                    cp -r \"$LATEST\" \"$DEST_PATH\"
                                else
                                    echo \"⚠️ No valid non-_rev_ backup found to restore for $DEST_PATH\"
                                fi

                                echo \"🧹 Cleaning up old _rev_ backups...\"
                                ls -dt ${FILE_NAME}_rev_* 2>/dev/null | tail -n +3 | xargs -r rm -rf
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

                        #ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            #CONTAINERS=\\$(sudo docker ps -aq)
                            #if [ -n \\\"\\$CONTAINERS\\\" ]; then
                                #echo \\\"Stopping containers...\\\"
                                #sudo docker stop \\$CONTAINERS
                                #echo \\\"Removing containers...\\\"
                                #sudo docker rm \\$CONTAINERS
                            #else
                                #echo \\\"No running containers to stop/remove.\\\"
                            fi
                            #echo \\\"Recreating containers with docker-compose...\\\"
                            #cd ${BASE_PATH}
                            #sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
