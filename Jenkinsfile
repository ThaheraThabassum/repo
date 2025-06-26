pipeline {
    agent any

    environment {
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        DEST_TMP_PATH = "/home/thahera"
        UI_DEPLOY_PATH = "/opt/lampp"
        UI_FOLDER_NAME = "kmb"
    }

    stages {
        stage('Read Deployment Zip File Names') {
            steps {
                script {
                    def lines = readFile('ui_deploy_filenames.txt').readLines()
                    env.ZIP_FILE_NAME = lines[0].trim()
                    env.USERMGMT_ZIP_NAME = lines[1].trim()
                    env.MASTERDATA_ZIP_NAME = lines[2].trim()
                    env.LOCAL_ZIP_PATH = "${DEST_TMP_PATH}/${env.ZIP_FILE_NAME}"

                    echo "UI Zip: ${env.ZIP_FILE_NAME}"
                    echo "Usermanagement Zip: ${env.USERMGMT_ZIP_NAME}"
                    echo "Masterdata Zip: ${env.MASTERDATA_ZIP_NAME}"
                }
            }
        }

        stage('Transfer UI Zip File') {
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    sh """
                        echo "Generating timestamp..."
                        TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)
                        echo \$TIMESTAMP > timestamp.txt

                        echo "Copying UI zip file from local to UAT server..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${ZIP_FILE_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/

                        echo "Copying usermanagement zip..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${USERMGMT_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/

                        echo "Copying masterdata zip..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${MASTERDATA_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                    """
                }
            }
        }

        stage('Unzip and Deploy UI on UAT') {
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
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

                            echo "Renaming original zip file with date+time suffix..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH}
                                FILE="${ZIP_FILE_NAME}"
                                TIMESTAMP="${timestamp}"
                                BASE_NAME="\${FILE%.zip}"
                                if [ -f "\$FILE" ]; then
                                    sudo mv "\$FILE" "\${BASE_NAME}_\${TIMESTAMP}.zip"
                                    echo "Zip file renamed to: \${BASE_NAME}_\${TIMESTAMP}.zip"
                                else
                                    echo "Zip file not found to rename."
                                fi
                            '
                        """
                    }
                }
            }
        }
    }
}
