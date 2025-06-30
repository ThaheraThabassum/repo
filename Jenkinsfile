pipeline {
    agent any

    environment {
        FILES_LIST_FILE = "files_to_revert.txt"
        REMOTE_USER = "thahera"
        REMOTE_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        DEST_BASE_PATH = "/home/ubuntu/ACE-Camunda-DevOps"
    }

    stages {
        stage('Direct Revert on DEST Server') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''#!/bin/bash
                        set -e
                        echo "📄 Reading files from ${FILES_LIST_FILE}..."

                        while IFS= read -r FILE_PATH || [ -n "$FILE_PATH" ]; do
                            [[ -z "$FILE_PATH" ]] && continue

                            TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                            DEST_PATH="${DEST_BASE_PATH}/$FILE_PATH"
                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "======== 🔄 Reverting: $FILE_PATH ========"

                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST <<EOF
                                set -e
                                cd "$DEST_DIR"

                                if [ -e "$FILE_NAME" ]; then
                                    echo "🛡️ Creating _rev_ backup..."
                                    echo "1234" | sudo -S mv "$FILE_NAME" "${FILE_NAME}_rev_${TIMESTAMP}"
                                else
                                    echo "⚠️ $FILE_NAME does not exist, skipping _rev_ backup."
                                fi

                                echo "🔍 Looking for latest non-_rev_ backup..."
                                BACKUP=\$(ls -1t ${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | head -n1)

                                if [ -n "\$BACKUP" ]; then
                                    echo "🔁 Restoring \$BACKUP → $FILE_NAME"
                                    echo "1234" | sudo -S mv "\$BACKUP" "$FILE_NAME"
                                else
                                    echo "⚠️ No valid backup found for $FILE_NAME"
                                fi

                                echo "🧹 Cleaning old _rev_ backups..."
                                ls -1t ${FILE_NAME}_rev_* 2>/dev/null | tail -n +2 | xargs -r sudo rm -rf
EOF

                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Restart Docker on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "🔄 Restarting Docker containers on DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            CONTAINERS=$(sudo docker ps -aq)
                            if [ -n \"$CONTAINERS\" ]; then
                                echo \"Stopping containers...\"
                                #sudo docker stop $CONTAINERS
                                echo \"Removing containers...\"
                                #sudo docker rm $CONTAINERS
                            else
                                echo \"No running containers to stop/remove.\"
                            fi
                            echo \"Bringing up containers using docker-compose...\"
                            cd ${DEST_BASE_PATH}
                            #sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
