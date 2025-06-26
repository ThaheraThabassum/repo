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
                    def filePath = 'ui_deploy_filenames.txt'
                    def lines = readFile(filePath).readLines().findAll { it?.trim() }

                    for (line in lines) {
                        def parts = line.split('=', 2)
                        if (parts.size() == 2) {
                            def key = parts[0].trim().toUpperCase()
                            def value = parts[1].trim()

                            if (key == 'UI') {
                                env.ZIP_FILE_NAME = value
                                env.LOCAL_ZIP_PATH = "${DEST_TMP_PATH}/${value}"
                            } else if (key == 'USERMANAGEMENT') {
                                env.USERMGMT_ZIP_NAME = value
                            } else if (key == 'MASTERDATA') {
                                env.MASTERDATA_ZIP_NAME = value
                            }
                        }
                    }

                    if (!env.ZIP_FILE_NAME) {
                        echo "\u26a0 UI zip file name not provided. UI deployment will be skipped."
                    } else {
                        echo "\u2714 UI Zip: ${env.ZIP_FILE_NAME}"
                    }

                    if (env.USERMGMT_ZIP_NAME) {
                        echo "\u2714 Usermanagement Zip: ${env.USERMGMT_ZIP_NAME}"
                    }

                    if (env.MASTERDATA_ZIP_NAME) {
                        echo "\u2714 Masterdata Zip: ${env.MASTERDATA_ZIP_NAME}"
                    }
                }
            }
        }

        stage('Transfer UI Zip File') {
            when {
                expression { return env.ZIP_FILE_NAME }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    sh """
                        echo "Generating timestamp..."
                        TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)
                        echo \$TIMESTAMP > timestamp.txt

                        echo "Copying UI zip file from local to UAT server..."
                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${ZIP_FILE_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/

                        ${env.USERMGMT_ZIP_NAME ? "echo 'Copying usermanagement zip...'\nscp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.USERMGMT_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/" : ""}

                        ${env.MASTERDATA_ZIP_NAME ? "echo 'Copying masterdata zip...'\nscp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.MASTERDATA_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/" : ""}
                    """
                }
            }
        }

        stage('Unzip and Deploy UI on UAT') {
            when {
                expression { return env.ZIP_FILE_NAME }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()

                        sh """
                            echo "Unzipping UI build on UAT server..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${DEST_TMP_PATH} && sudo unzip -o ${ZIP_FILE_NAME}"

                            echo "Taking backup of existing UI folder..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH} && [ -d ${UI_FOLDER_NAME} ] && sudo mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_\${timestamp} || echo 'No existing UI folder to backup.'"

                            echo "Deploying new UI folder..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/"

                            echo "Backing up pdf directory in new UI..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets && [ -d pdf ] && sudo mv pdf pdf_\${timestamp} || echo 'No pdf folder found to backup.'"

                            echo "Restoring pdf, usermanagement, masterdata from current backup..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                set -e
                                cd ${UI_DEPLOY_PATH}
                                BACKUP_NAME="${UI_FOLDER_NAME}_\${timestamp}"
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

        stage('Deploy Usermanagement') {
            when {
                expression { return env.USERMGMT_ZIP_NAME }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()

                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH}
                                sudo unzip -o ${env.USERMGMT_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/htdocs/kmb
                                [ -d usermanagement ] && sudo mv usermanagement usermanagement_\${timestamp} || echo "No existing usermanagement folder to backup."

                                sudo mv ${DEST_TMP_PATH}/usermanagement .

                                [ -d usermanagement_\${timestamp}/assets/user_files ] && sudo cp -r usermanagement_\${timestamp}/assets/user_files usermanagement/assets/ || echo "No user_files to restore."

                                ls -td usermanagement_*/ 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf

                                sudo chmod -R 777 usermanagement
                            '
                        """
                    }
                }
            }
        }

        stage('Deploy Masterdata') {
            when {
                expression { return env.MASTERDATA_ZIP_NAME }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()

                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH}
                                sudo unzip -o ${env.MASTERDATA_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/htdocs/kmb
                                [ -d masterdata ] && sudo mv masterdata masterdata_\${timestamp} || echo "No existing masterdata folder to backup."

                                sudo mv ${DEST_TMP_PATH}/masterdata .

                                ls -td masterdata_*/ 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf

                                sudo chmod -R 777 masterdata
                            '
                        """
                    }
                }
            }
        }
    }
}
