pipeline {
    agent any

    environment {
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        ZIP_FILE_NAME = "kmb_UI_UAT.zip"
        LOCAL_ZIP_PATH = "/home/ubuntu/${ZIP_FILE_NAME}"
        DEST_TMP_PATH = "/home/thahera"
        UI_DEPLOY_PATH = "/opt/lampp"
        UI_FOLDER_NAME = "kmb"
    }

    stages {
        stage('Transfer UI Zip File') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Copying UI zip file from local to UAT server..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${LOCAL_ZIP_PATH} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                    """
                }
            }
        }

        stage('Unzip and Deploy UI on UAT') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)
                        cd ${DEST_TMP_PATH}

                        echo "Unzipping UI build on UAT server..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${DEST_TMP_PATH} && unzip -o ${ZIP_FILE_NAME}"

                        echo "Taking backup of existing UI folder..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH} && [ -d ${UI_FOLDER_NAME} ] && mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_\${TIMESTAMP} || echo 'No existing UI folder to backup.'"

                        echo "Deploying new UI folder..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/"

                        echo "Backing up pdf directory in new UI..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets && [ -d pdf ] && mv pdf pdf_\${TIMESTAMP} || echo 'No pdf folder found to backup.'"

                        echo "Restoring pdf, usermanagement, masterdata from backup..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c "'
                            cd ${UI_DEPLOY_PATH}
                            BACKUP_DIR=\$(ls -td ${UI_FOLDER_NAME}_*/ | head -1 | tr -d /)
                            if [ -d \$BACKUP_DIR ]; then
                                cp -r \$BACKUP_DIR/assets/pdf ${UI_FOLDER_NAME}/assets/ || echo 'No pdf found in backup'
                                cp -r \$BACKUP_DIR/usermanagement ${UI_FOLDER_NAME}/ || echo 'No usermanagement found in backup'
                                cp -r \$BACKUP_DIR/masterdata ${UI_FOLDER_NAME}/ || echo 'No masterdata found in backup'
                            else
                                echo 'No backup directory to restore from.'
                            fi
                        '"

                        echo "Setting permissions to 777..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod -R 777 ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}"
                    """
                }
            }
        }
    }
}
