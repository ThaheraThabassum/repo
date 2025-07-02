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
                    def lines = readFile('ui_deploy_filenames.txt').readLines().findAll { it?.trim() }
                    for (line in lines) {
                        def (key, value) = line.split('=', 2)*.trim()
                        switch (key?.toUpperCase()) {
                            case 'UI': env.ZIP_FILE_NAME = value; break
                            case 'USERMANAGEMENT': env.USERMGMT_ZIP_NAME = value; break
                            case 'MASTERDATA': env.MASTERDATA_ZIP_NAME = value; break
                        }
                    }
                    env.TIMESTAMP = new Date().format("dd_MM_yy_HH_mm_ss")
                    writeFile file: 'timestamp.txt', text: env.TIMESTAMP
                }
            }
        }

        stage('Check Revert Flags') {
            steps {
                script {
                    def lines = readFile('ui_revert_files.txt').readLines().findAll { it?.trim() }
                    env.REVERT_UI = "false"
                    env.REVERT_USERMGMT = "false"
                    env.REVERT_MASTERDATA = "false"
                    for (line in lines) {
                        def (key, value) = line.split('=', 2)*.trim()
                        switch (key?.toUpperCase()) {
                            case 'UI': env.REVERT_UI = value.toLowerCase(); break
                            case 'USERMANAGEMENT': env.REVERT_USERMGMT = value.toLowerCase(); break
                            case 'MASTERDATA': env.REVERT_MASTERDATA = value.toLowerCase(); break
                        }
                    }
                }
            }
        }

        stage('Revert Selected Modules') {
            when {
                anyOf {
                    expression { env.REVERT_UI == 'true' }
                    expression { env.REVERT_USERMGMT == 'true' }
                    expression { env.REVERT_MASTERDATA == 'true' }
                }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        def timestamp = env.TIMESTAMP
                        sh """
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} <<EOF
                            export TIMESTAMP=${timestamp}
                            cd ${UI_DEPLOY_PATH}

                            if [ "${env.REVERT_USERMGMT}" = "true" ]; then
                                echo "🔄 Reverting Usermanagement..."
                                cd ${UI_FOLDER_NAME}
                                if [ -d usermanagement ]; then
                                    sudo mv usermanagement usermanagement_revert_\$TIMESTAMP
                                    latest=
                                    latest=\$(ls -td usermanagement_* 2>/dev/null | head -n1)
                                    if [ -d "\$latest" ]; then
                                        sudo mv "\$latest" usermanagement
                                        sudo chmod -R 777 usermanagement
                                    fi
                                fi
                                cd ..
                            fi

                            if [ "${env.REVERT_MASTERDATA}" = "true" ]; then
                                echo "🔄 Reverting Masterdata..."
                                cd ${UI_FOLDER_NAME}
                                if [ -d masterdata ]; then
                                    sudo mv masterdata masterdata_revert_\$TIMESTAMP
                                    latest=\$(ls -td masterdata_* 2>/dev/null | head -n1)
                                    if [ -d "\$latest" ]; then
                                        sudo mv "\$latest" masterdata
                                        sudo chmod -R 777 masterdata
                                    fi
                                fi
                                cd ..
                            fi

                            if [ "${env.REVERT_UI}" = "true" ]; then
                                echo "🔄 Reverting UI..."
                                if [ -d ${UI_FOLDER_NAME} ]; then
                                    sudo mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_revert_\$TIMESTAMP
                                    latest=\$(ls -td ${UI_FOLDER_NAME}_* 2>/dev/null | head -n1)
                                    if [ -d "\$latest" ]; then
                                        sudo mv "\$latest" ${UI_FOLDER_NAME}
                                    fi
                                    [ -d ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ] && sudo mv ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ${UI_FOLDER_NAME}/assets/ || true
                                    cd ${UI_FOLDER_NAME}
                                    [ -d usermanagement ] && sudo mv usermanagement usermanagement_old_\$TIMESTAMP || true
                                    [ -d masterdata ] && sudo mv masterdata masterdata_old_\$TIMESTAMP || true
                                    [ -d ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/usermanagement ] && sudo cp -r ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/usermanagement . || true
                                    [ -d ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/masterdata ] && sudo cp -r ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/masterdata . || true
                                    cd ..
                                    sudo chmod -R 777 ${UI_FOLDER_NAME}
                                fi
                            fi

                            echo "🪩 Cleaning old revert backups..."
                            find . -maxdepth 1 -type d -name "${UI_FOLDER_NAME}_revert_*" ! -name "${UI_FOLDER_NAME}_revert_\$TIMESTAMP" -exec sudo rm -rf {} +
                            find ${UI_FOLDER_NAME} -maxdepth 1 -type d -name "usermanagement_revert_*" ! -name "usermanagement_revert_\$TIMESTAMP" -exec sudo rm -rf {} +
                            find ${UI_FOLDER_NAME} -maxdepth 1 -type d -name "masterdata_revert_*" ! -name "masterdata_revert_\$TIMESTAMP" -exec sudo rm -rf {} +
EOF
                        """
                    }
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
                                    [ -d "\$BACKUP/assets/pdf" ] && sudo mv "\$BACKUP/assets/pdf" "${UI_FOLDER_NAME}/assets/" || true
                                    [ -d "\$BACKUP/usermanagement" ] && sudo cp -r "\$BACKUP/usermanagement" "${UI_FOLDER_NAME}/" || true
                                    [ -d "\$BACKUP/masterdata" ] && sudo cp -r "\$BACKUP/masterdata" "${UI_FOLDER_NAME}/" || true
                                fi

                                cd ${UI_DEPLOY_PATH}
                                ls -td ${UI_FOLDER_NAME}_*/ | tail -n +4 | xargs -r sudo rm -rf
                                sudo chmod -R 777 ${UI_FOLDER_NAME}
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
