pipeline {
    agent any

    environment {
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        ZIP_FILE_NAME = "kmb_UI_UAT.zip"
        LOCAL_ZIP_PATH = "/home/thahera/${ZIP_FILE_NAME}"
        DEST_TMP_PATH = "/home/thahera"
        UI_DEPLOY_PATH = "/opt/lampp"
        UI_FOLDER_NAME = "kmb"
    }

    stages {
        stage('Transfer UI Zip File') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Generating timestamp..."
                        TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)
                        echo \$TIMESTAMP > timestamp.txt

                        echo "Copying UI zip file from local to UAT server..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${LOCAL_ZIP_PATH} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                    """
                }
            }
        }

        stage('Unzip and Deploy UI on UAT') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()

                        sh """
                            echo "Unzipping UI build on UAT server..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${DEST_TMP_PATH} && sudo unzip -o ${ZIP_FILE_NAME}"

                            echo "Taking backup of existing UI folder..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH} && [ -d ${UI_FOLDER_NAME} ] && sudo mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_${timestamp} || echo 'No existing UI folder to backup.'"

                            echo "Deploying new UI folder..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/"

                            echo "Backing up pdf directory in new UI..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets && [ -d pdf ] && sudo mv pdf pdf_${timestamp} || echo 'No pdf folder found to backup.'"

                            echo "Restoring pdf, usermanagement, masterdata from current backup..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                set -e
                                cd ${UI_DEPLOY_PATH}
                                BACKUP_NAME="${UI_FOLDER_NAME}_${timestamp}"
                                echo "Looking for backup: \$BACKUP_NAME"

                                if [ -d "\$BACKUP_NAME" ]; then
                                    [ -d "\$BACKUP_NAME/assets/pdf" ] && sudo cp -r "\$BACKUP_NAME/assets/pdf" "${UI_FOLDER_NAME}/assets/" || echo "No pdf folder in backup"
                                    [ -d "\$BACKUP_NAME/usermanagement" ] && sudo cp -r "\$BACKUP_NAME/usermanagement" "${UI_FOLDER_NAME}/" || echo "No usermanagement in backup"
                                    [ -d "\$BACKUP_NAME/masterdata" ] && sudo cp -r "\$BACKUP_NAME/masterdata" "${UI_FOLDER_NAME}/" || echo "No masterdata in backup"
                                else
                                    echo "Backup folder \$BACKUP_NAME not found!"
                                fi
                            '

                            echo "Cleaning old UI backups (retain only latest 3)..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${UI_DEPLOY_PATH}
                                ls -td ${UI_FOLDER_NAME}_*/ 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf
                            '

                            echo "Setting permissions to 777..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod -R 777 ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}"
                        """
                    }
                }
            }
        }
    }
}
