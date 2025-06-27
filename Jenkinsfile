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
                        echo "📘 Reading files to revert from ${FILES_LIST_FILE}..."

                        while IFS= read -r FILE_PATH || [ -n "$FILE_PATH" ]; do
                            [[ -z "$FILE_PATH" ]] && continue

                            TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                            DEST_PATH="${DEST_BASE_PATH}/${FILE_PATH}"
                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "======================================="
                            echo "🔁 Reverting: $FILE_PATH"
                            echo "======================================="

                            # Step 1: Backup current file/folder to _rev_
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                if [ -e '$DEST_PATH' ]; then
                                    echo '🗄️  Creating _rev_ backup...'
                                    mv '$DEST_PATH' '${DEST_PATH}_rev_${TIMESTAMP}'
                                else
                                    echo '⚠️  $DEST_PATH does not exist, skipping backup.'
                                fi
                            "

                            # Step 2: Restore latest *_timestamp backup (excluding _rev_)
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                cd '$DEST_DIR'
                                LATEST=\$(ls -td ${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | head -n1 || true)
                                if [ -n \"\$LATEST\" ]; then
                                    echo '♻️  Restoring \$LATEST to $DEST_PATH...'
                                    mv \"\$LATEST\" \"$DEST_PATH\"
                                else
                                    echo '❌ No valid backup found for $DEST_PATH'
                                fi
                            "

                            # Step 3: Cleanup old _rev_ backups (keep only latest)
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                cd '$DEST_DIR'
                                echo '🧹 Cleaning up old _rev_ backups...'
                                ls -td ${FILE_NAME}_rev_* 2>/dev/null | tail -n +2 | xargs -r rm -rf
                            "

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

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            CONTAINERS=\\$(sudo docker ps -aq)
                            if [ -n \\\"\\$CONTAINERS\\\" ]; then
                                echo \\\"🛑 Stopping containers...\\\"
                                sudo docker stop \\$CONTAINERS
                                echo \\\"🗑️  Removing containers...\\\"
                                sudo docker rm \\$CONTAINERS
                            else
                                echo \\\"✅ No running containers to stop/remove.\\\"
                            fi
                            echo \\\"🚀 Restarting with docker-compose...\\\"
                            cd ${DEST_BASE_PATH}
                            sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
