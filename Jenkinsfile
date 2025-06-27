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
        stage('Revert Files/Folders on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''#!/bin/bash
                        set -e
                        echo "Reading files from ${FILES_LIST_FILE}..."

                        while IFS= read -r FILE_PATH || [ -n "$FILE_PATH" ]; do
                            [[ -z "$FILE_PATH" ]] && continue

                            TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                            DEST_PATH="$DEST_BASE_PATH/$FILE_PATH"
                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "======== 🔄 Reverting: $FILE_PATH ========"

                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
                                if [ -e '$DEST_PATH' ]; then
                                    echo '🛡️ Creating _rev_ backup...'
                                    sudo mv '$DEST_PATH' '${DEST_PATH}_rev_${TIMESTAMP}'
                                else
                                    echo '⚠️ $DEST_PATH does not exist, skipping backup.'
                                fi
                            "

                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
                                cd '$DEST_DIR'
                                echo '🔍 Looking for latest non-_rev_ backup...'
                                LATEST=\$(ls -td ${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | head -n 1 || true)
                                if [ -n \"\$LATEST\" ]; then
                                    echo \"✅ Restoring \$LATEST -> $DEST_PATH\"
                                    sudo mv \"\$LATEST\" \"$DEST_PATH\"
                                else
                                    echo '❌ No valid backup found for $DEST_PATH'
                                fi
                            "

                            ssh -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "
                                cd '$DEST_DIR'
                                echo '🧹 Cleaning old _rev_ backups...'
                                ls -td ${FILE_NAME}_rev_* 2>/dev/null | tail -n +2 | xargs -r sudo rm -rf
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
                        echo "🔄 Restarting Docker containers..."
                        #ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            3CONTAINERS=\\$(sudo docker ps -aq)
                            #if [ -n \\\"\\$CONTAINERS\\\" ]; then
                                #sudo docker stop \\$CONTAINERS
                                #sudo docker rm \\$CONTAINERS
                            #else
                                #echo \\\"No running containers to stop/remove.\\\"
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
