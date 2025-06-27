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
                        echo "Reading files to revert from ${FILES_LIST_FILE}..."

                        while IFS= read -r FILE_PATH || [ -n "$FILE_PATH" ]; do
                            [[ -z "$FILE_PATH" ]] && continue
                            
                            TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                            DEST_PATH="${DEST_BASE_PATH}/${FILE_PATH}"
                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "========== Reverting: $FILE_PATH =========="

                            # Backup current file/folder to _rev_
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                if [ -e '$DEST_PATH' ]; then
                                    echo 'Creating _rev_ backup...'
                                    mv '$DEST_PATH' '${DEST_PATH}_rev_${TIMESTAMP}'
                                else
                                    echo '❌ $DEST_PATH does not exist, skipping backup.'
                                fi
                            "

                            # Restore latest timestamped backup (non-_rev_)
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                cd '$DEST_DIR'
                                LATEST=\$(ls -td ${FILE_NAME}_* | grep -v '_rev_' | head -n1 || true)
                                if [ -n \"\$LATEST\" ]; then
                                    echo 'Restoring \$LATEST to $DEST_PATH...'
                                    mv \"\$LATEST\" \"$DEST_PATH\"
                                else
                                    echo '⚠️ No non-_rev_ backup found for $DEST_PATH'
                                fi
                            "

                            # Cleanup older _rev_ backups (keep 1 latest)
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "
                                cd '$DEST_DIR'
                                echo 'Cleaning up old _rev_ backups...'
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
                        echo "Restarting Docker containers on DEST_HOST..."
                        #ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "'
                            #CONTAINERS=\\$(sudo docker ps -aq)
                            #if [ -n \\\"\\$CONTAINERS\\\" ]; then
                                #sudo docker stop \\$CONTAINERS
                                #sudo docker rm \\$CONTAINERS
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
