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
        HTDOCS_PATH = "/opt/lampp/htdocs/${UI_FOLDER_NAME}"
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
                        echo "⚠ UI zip file name not provided. UI deployment will be skipped."
                    } else {
                        echo "✔ UI Zip: ${env.ZIP_FILE_NAME}"
                    }

                    if (env.USERMGMT_ZIP_NAME) {
                        echo "✔ Usermanagement Zip: ${env.USERMGMT_ZIP_NAME}"
                    }

                    if (env.MASTERDATA_ZIP_NAME) {
                        echo "✔ Masterdata Zip: ${env.MASTERDATA_ZIP_NAME}"
                    }
                }
            }
        }

        stage('Transfer Files to UAT Server') {
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    sh '''
                        echo "Generating timestamp..."
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        echo $TIMESTAMP > timestamp.txt
                    '''

                    if (env.ZIP_FILE_NAME) {
                        sh """
                            echo "Copying UI zip file..."
                            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${ZIP_FILE_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                        """
                    }
                    if (env.USERMGMT_ZIP_NAME) {
                        sh """
                            echo "Copying Usermanagement zip..."
                            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${USERMGMT_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                        """
                    }
                    if (env.MASTERDATA_ZIP_NAME) {
                        sh """
                            echo "Copying Masterdata zip..."
                            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${MASTERDATA_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                        """
                    }
                }
            }
        }

        stage('Deploy UI') {
            when { expression { return env.ZIP_FILE_NAME } }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH} && sudo unzip -o ${ZIP_FILE_NAME}
                                cd ${UI_DEPLOY_PATH}
                                [ -d ${UI_FOLDER_NAME} ] && sudo mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_\${TIMESTAMP} || echo "No UI folder to backup"
                                sudo mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/
                                cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets && [ -d pdf ] && sudo mv pdf pdf_\${TIMESTAMP} || echo "No pdf folder to backup"

                                cd ${UI_DEPLOY_PATH}
                                BACKUP_NAME="${UI_FOLDER_NAME}_\${TIMESTAMP}"
                                [ -d "\$BACKUP_NAME/assets/pdf" ] && sudo cp -r "\$BACKUP_NAME/assets/pdf" "${UI_FOLDER_NAME}/assets/" || echo "No pdf in backup"
                                [ -d "\$BACKUP_NAME/usermanagement" ] && sudo cp -r "\$BACKUP_NAME/usermanagement" "${UI_FOLDER_NAME}/" || echo "No usermanagement in backup"
                                [ -d "\$BACKUP_NAME/masterdata" ] && sudo cp -r "\$BACKUP_NAME/masterdata" "${UI_FOLDER_NAME}/" || echo "No masterdata in backup"

                                ls -td ${UI_FOLDER_NAME}_*/ 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf
                                sudo chmod -R 777 ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}
                            '
                        """
                    }
                }
            }
        }

        stage('Deploy Usermanagement') {
            when { expression { return env.USERMGMT_ZIP_NAME } }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH} && sudo unzip -o ${USERMGMT_ZIP_NAME}
                                cd ${HTDOCS_PATH}
                                [ -d usermanagement ] && sudo mv usermanagement usermanagement_\${TIMESTAMP} || echo "No usermanagement folder to backup"
                                sudo mv ${DEST_TMP_PATH}/usermanagement ${HTDOCS_PATH}/
                                sudo cp -r usermanagement_\${TIMESTAMP}/assets/user_files usermanagement/assets/ || echo "No user_files to copy"
                                ls -td usermanagement_*/ 2>/dev/null | tail -n +4 | xargs -r sudo rm -rf
                                sudo chmod -R 777 usermanagement
                            '
                        """
                    }
                }
            }
        }

        stage('Deploy Masterdata') {
            when { expression { return env.MASTERDATA_ZIP_NAME } }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                cd ${DEST_TMP_PATH} && sudo unzip -o ${MASTERDATA_ZIP_NAME}
                                cd ${HTDOCS_PATH}
                                [ -d masterdata ] && sudo mv masterdata masterdata_\${TIMESTAMP} || echo "No masterdata folder to backup"
                                sudo mv ${DEST_TMP_PATH}/masterdata ${HTDOCS_PATH}/
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
