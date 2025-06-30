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
                            DEST_PATH="$DEST_BASE_PATH/$FILE_PATH"
                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "======== 🔄 Reverting: $FILE_PATH ========"

                            # Step 1: Backup current as _rev_
                            echo "🛡️ Backing up current file/folder as _rev_"
                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST <<EOF
                                if [ -e '$DEST_PATH' ]; then
                                    echo '1234' | sudo -S mv '$DEST_PATH' '${DEST_PATH}_rev_${TIMESTAMP}'
                                else
                                    echo "⚠️ $DEST_PATH does not exist, skipping backup."
                                fi
EOF

                            # Step 2: Restore latest non-_rev_ backup
                            echo "🔍 Looking for latest non-_rev_ backup..."
                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST <<EOF
                                cd "$DEST_DIR"
                                LATEST=\$(ls -1t | grep "^${FILE_NAME}_" | grep -v "_rev_" | head -n1)
                                if [ -n "\$LATEST" ]; then
                                    echo "🔁 Restoring \$LATEST to $DEST_PATH"
                                    echo '1234' | sudo -S mv "\$LATEST" "$DEST_PATH"
                                else
                                    echo "⚠️ No valid backup found for $DEST_PATH"
                                fi
EOF

                            # Step 3: Clean older _rev_ backups
                            echo "🧹 Cleaning old _rev_ backups (keeping latest one)..."
                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST <<EOF
                                cd "$DEST_DIR"
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
                        echo "♻️ Restarting Docker containers on DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            CONTAINERS=$(sudo docker ps -aq)
                            if [ -n \"$CONTAINERS\" ]; then
                                echo \"Stopping containers...\"
                                #sudo docker stop $CONTAINERS
                                echo \"Removing containers...\"
                                #sudo docker rm $CONTAINERS
                            fi
                            cd ${DEST_BASE_PATH}
                            #sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
