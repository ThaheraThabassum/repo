pipeline {
    agent any

    environment {
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "3.7.132.76"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        DEST_TMP_PATH = "/home/thahera"
        UI_DEPLOY_PATH = "/var/www/"
        UI_FOLDER_NAME = "kmb"
        SUDO_PASS = "1234"
    }

    stages {
        stage('Read Deployment Zip File Names') {
            steps {
                script {
                    def lines = readFile('ui_deploy_filenames.txt').readLines().findAll { it?.trim() }
                    lines.each { line ->
                        def parts = line.split('=')
                        if (parts.length == 2) {
                            def key = parts[0].trim().toUpperCase()
                            def value = parts[1].trim()
                            if (key == 'UI') env.ZIP_FILE_NAME = value
                            if (key == 'USERMANAGEMENT') env.USERMGMT_ZIP_NAME = value
                            if (key == 'MASTERDATA') env.MASTERDATA_ZIP_NAME = value
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
                    lines.each { line ->
                        def parts = line.split('=')
                        if (parts.length == 2) {
                            def key = parts[0].trim().toUpperCase()
                            def value = parts[1].trim().toLowerCase()
                            if (key == 'UI') env.REVERT_UI = value
                            if (key == 'USERMANAGEMENT') env.REVERT_USERMGMT = value
                            if (key == 'MASTERDATA') env.REVERT_MASTERDATA = value
                        }
                    }
                }
            }
        }

        stage('Revert Selected Modules') {
            when {
                anyOf {
                    expression { return env.REVERT_UI == 'true' }
                    expression { return env.REVERT_USERMGMT == 'true' }
                    expression { return env.REVERT_MASTERDATA == 'true' }
                }
            }
            steps {
                sshagent(credentials: [env.SSH_KEY]) {
                    script {
                        sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} << 'EOF'
                        export TIMESTAMP=${env.TIMESTAMP}
                        export SUDO_PASS=${SUDO_PASS}
                        cd ${UI_DEPLOY_PATH}

                        if [ "${env.REVERT_USERMGMT}" = "true" ]; then
                            echo "🔄 Reverting Usermanagement..."
                            cd ${UI_FOLDER_NAME}
                            [ -d usermanagement ] && echo "\$SUDO_PASS" | sudo -S mv usermanagement usermanagement_revert_\$TIMESTAMP || true
                            latest=\$(ls -td usermanagement_* 2>/dev/null | grep -v revert | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" usermanagement
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 usermanagement
                            fi
                            cd ..
                        fi

                        if [ "${env.REVERT_MASTERDATA}" = "true" ]; then
                            echo "🔄 Reverting Masterdata..."
                            cd ${UI_FOLDER_NAME}
                            [ -d masterdata ] && echo "\$SUDO_PASS" | sudo -S mv masterdata masterdata_revert_\$TIMESTAMP || true
                            latest=\$(ls -td masterdata_* 2>/dev/null | grep -v revert | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" masterdata
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 masterdata
                            fi
                            cd ..
                        fi

                        if [ "${env.REVERT_UI}" = "true" ]; then
                            echo "🔄 Reverting UI..."
                            [ -d ${UI_FOLDER_NAME} ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_revert_\$TIMESTAMP || true
                            latest=\$(ls -td ${UI_FOLDER_NAME}_* 2>/dev/null | grep -v revert | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" ${UI_FOLDER_NAME}
                            fi

                            echo "↩️ Restoring pdf folder from UI revert..."
                            [ -d ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ${UI_FOLDER_NAME}/assets/ || true

                            echo "📁 Backing up existing usermanagement and masterdata before restoring from UI revert..."
                            cd ${UI_FOLDER_NAME}
                            [ -d usermanagement ] && echo "\$SUDO_PASS" | sudo -S mv usermanagement usermanagement_old_\$TIMESTAMP || true
                            [ -d masterdata ] && echo "\$SUDO_PASS" | sudo -S mv masterdata masterdata_old_\$TIMESTAMP || true

                            echo "📁 Copying usermanagement and masterdata from UI revert..."
                            [ -d ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/usermanagement ] && echo "\$SUDO_PASS" | sudo -S cp -r ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/usermanagement . || true
                            [ -d ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/masterdata ] && echo "\$SUDO_PASS" | sudo -S cp -r ../${UI_FOLDER_NAME}_revert_\$TIMESTAMP/masterdata . || true

                            cd ${UI_DEPLOY_PATH}
                            echo "\$SUDO_PASS" | sudo -S chmod -R 777 ${UI_FOLDER_NAME}
                        fi

                        if [ "${env.REVERT_UI}" = "true" ]; then
                            echo "🧹 Cleaning old UI revert backups..."
                            find . -maxdepth 1 -type d -name "${UI_FOLDER_NAME}_revert_*" ! -name "${UI_FOLDER_NAME}_revert_\$TIMESTAMP" -exec echo "\$SUDO_PASS" | sudo -S rm -rf {} +
                        fi

                        if [ "${env.REVERT_USERMGMT}" = "true" ]; then
                            echo "🧹 Cleaning old Usermanagement revert backups..."
                            find ${UI_FOLDER_NAME} -maxdepth 1 -type d -name "usermanagement_revert_*" ! -name "usermanagement_revert_\$TIMESTAMP" -exec echo "\$SUDO_PASS" | sudo -S rm -rf {} +
                        fi

                        if [ "${env.REVERT_MASTERDATA}" = "true" ]; then
                            echo "🧹 Cleaning old Masterdata revert backups..."
                            find ${UI_FOLDER_NAME} -maxdepth 1 -type d -name "masterdata_revert_*" ! -name "masterdata_revert_\$TIMESTAMP" -exec echo "\$SUDO_PASS" | sudo -S rm -rf {} +
                        fi
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
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.ZIP_FILE_NAME}

                                cd ${UI_DEPLOY_PATH}
                                [ -d ${UI_FOLDER_NAME} ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_${timestamp} || echo "No existing UI to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/

                                cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets
                                [ -d pdf ] && echo "\$SUDO_PASS" | sudo -S mv pdf pdf_${timestamp} || echo "No pdf to backup"

                                cd ${UI_DEPLOY_PATH}
                                BACKUP=${UI_FOLDER_NAME}_${timestamp}
                                if [ -d "\$BACKUP" ]; then
                                    [ -d "\$BACKUP/assets/pdf" ] && echo "\$SUDO_PASS" | sudo -S mv "\$BACKUP/assets/pdf" "${UI_FOLDER_NAME}/assets/" || true
                                    [ -d "\$BACKUP/usermanagement" ] && echo "\$SUDO_PASS" | sudo -S cp -r "\$BACKUP/usermanagement" "${UI_FOLDER_NAME}/" || true
                                    [ -d "\$BACKUP/masterdata" ] && echo "\$SUDO_PASS" | sudo -S cp -r "\$BACKUP/masterdata" "${UI_FOLDER_NAME}/" || true
                                fi

                                cd ${UI_DEPLOY_PATH}
                                ls -td ${UI_FOLDER_NAME}_*/ | tail -n +4 | xargs -r echo "\$SUDO_PASS" | sudo -S rm -rf
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 ${UI_FOLDER_NAME}
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
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.USERMGMT_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/kmb
                                [ -d usermanagement ] && echo "\$SUDO_PASS" | sudo -S mv usermanagement usermanagement_${timestamp} || echo "No existing usermanagement to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/usermanagement ${UI_DEPLOY_PATH}/kmb/
                                echo "\$SUDO_PASS" | sudo -S cp -r usermanagement_${timestamp}/assets/user_files usermanagement/assets/ || true

                                ls -td usermanagement_*/ | tail -n +4 | xargs -r echo "\$SUDO_PASS" | sudo -S rm -rf
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 usermanagement
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
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.MASTERDATA_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}/kmb
                                [ -d masterdata ] && echo "\$SUDO_PASS" | sudo -S mv masterdata masterdata_${timestamp} || echo "No existing masterdata to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/masterdata ${UI_DEPLOY_PATH}/kmb/

                                ls -td masterdata_*/ | tail -n +4 | xargs -r echo "\$SUDO_PASS" | sudo -S rm -rf
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 masterdata
                            '
                        """
                    }
                }
            }
        }
    }
}
