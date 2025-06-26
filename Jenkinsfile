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

                    TIMESTAMP = new Date().format("dd_MM_yy_HH_mm_ss")
                    writeFile file: 'timestamp.txt', text: TIMESTAMP

                    echo "✔ Timestamp: ${TIMESTAMP}"
                    if (env.ZIP_FILE_NAME) echo "✔ UI Zip: ${env.ZIP_FILE_NAME}"
                    if (env.USERMGMT_ZIP_NAME) echo "✔ Usermanagement Zip: ${env.USERMGMT_ZIP_NAME}"
                    if (env.MASTERDATA_ZIP_NAME) echo "✔ Masterdata Zip: ${env.MASTERDATA_ZIP_NAME}"
                }
            }
        }

        stage('Transfer Zip Files') {
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = readFile('timestamp.txt').trim()

                        if (env.ZIP_FILE_NAME) {
                            sh """
                                echo "Copying UI zip..."
                                scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.ZIP_FILE_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                            """
                        }

                        if (env.USERMGMT_ZIP_NAME) {
                            sh """
                                echo "Copying usermanagement zip..."
                                scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.USERMGMT_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                            """
                        }

                        if (env.MASTERDATA_ZIP_NAME) {
                            sh """
                                echo "Copying masterdata zip..."
                                scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.MASTERDATA_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                            """
                        }
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
                                cd ${DEST_TMP_PATH}
                                sudo unzip -o ${env.ZIP_FILE_NAME}

                                cd ${UI_DEPLOY_PATH}
                                [ -d ${UI_FOLDER_NAME} ] && sudo mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_${timestamp} || echo "No existing UI to backup"
                                sudo mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/

                                cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets
                                [ -d pdf ] && sudo mv pdf pdf_${timestamp} || echo "No pdf to backup"

                                cd ${UI_DEPLOY_PATH}
                                BACKUP=${UI_FOLDER_NAME}_${timestamp}
                                if [ -d "\$BACKUP" ]; then
                                    [ -d "\$BACKUP/assets/pdf" ] && sudo cp -r "\$BACKUP/assets/pdf" "${UI_FOLDER_NAME}/assets/" || true
                                    [ -d "\$BACKUP/usermanagement" ] && sudo cp -r "\$BACKUP/usermanagement" "${UI_FOLDER_NAME}/" || true
                                    [ -d "\$BACKUP/masterdata" ] && sudo cp -r "\$BACKUP/masterdata" "${UI_FOLDER_NAME}/" || true
                                fi

                                cd ${UI_DEPLOY_PATH}
                                ls -td ${UI_FOLDER_NAME}_*/ | tail -n +4 | xargs -r sudo rm -rf
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
                                cd ${DEST_TMP_PATH}
                                sudo unzip -o ${env.USERMGMT_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/kmb
                                [ -d usermanagement ] && sudo mv usermanagement usermanagement_${timestamp} || echo "No existing usermanagement to backup"
                                sudo mv ${DEST_TMP_PATH}/usermanagement ${UI_DEPLOY_PATH}/kmb/
                                sudo cp -r usermanagement_${timestamp}/assets/user_files usermanagement/assets/ || true

                                ls -td usermanagement_*/ | tail -n +4 | xargs -r sudo rm -rf
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
                                cd ${DEST_TMP_PATH}
                                sudo unzip -o ${env.MASTERDATA_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/kmb
                                [ -d masterdata ] && sudo mv masterdata masterdata_${timestamp} || echo "No existing masterdata to backup"
                                sudo mv ${DEST_TMP_PATH}/masterdata ${UI_DEPLOY_PATH}/kmb/

                                ls -td masterdata_*/ | tail -n +4 | xargs -r sudo rm -rf
                                sudo chmod -R 777 masterdata
                            '
                        """
                    }
                }
            }
        }
    }
}
