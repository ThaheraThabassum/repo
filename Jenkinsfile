pipeline {
    agent any

    environment {
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "3.7.132.76"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        DEST_TMP_PATH = "/home/thahera"
        UI_DEPLOY_PATH = "/var/www/html/"
        UI_FOLDER_NAME = "kmb"
        SUDO_PASS = "1234"
    }

    stages {
        stage('Set Custom Build ID') {
            steps {
                script {
                    def customId = String.format("KMBL%03d", currentBuild.number)
                    currentBuild.displayName = customId
                    echo "🔖 Deployment Build ID: ${customId}"
                }
            }
        }
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
                            [ -d usermanagement ] && echo "\$SUDO_PASS" | sudo -S mv usermanagement ../usermanagement_revert_\$TIMESTAMP || true
                            latest=\$(ls -td ../usermanagement_[0-9]* 2>/dev/null | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" usermanagement
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 usermanagement
                            fi
                            echo "🧹 Cleaning up old usermanagement revert backups..."
                            latest_revert=\$(basename \$(ls -td ../usermanagement_revert_* 2>/dev/null | head -n1))
                            ls -td ../usermanagement_revert_* 2>/dev/null | while read dir; do
                                base=\$(basename "\$dir")
                                if [ "\$base" != "\$latest_revert" ]; then
                                    echo "\$SUDO_PASS" | sudo -S rm -rf "\$dir"
                                fi
                            done
                            cd ..
                        fi

                        if [ "${env.REVERT_MASTERDATA}" = "true" ]; then
                            echo "🔄 Reverting Masterdata..."
                            cd ${UI_FOLDER_NAME}
                            [ -d masterdata ] && echo "\$SUDO_PASS" | sudo -S mv masterdata ../masterdata_revert_\$TIMESTAMP || true
                            latest=\$(ls -td ../masterdata_[0-9]* 2>/dev/null | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" masterdata
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 masterdata
                            fi
                            echo "🧹 Cleaning up old masterdata revert backups..."
                            latest_revert=\$(basename \$(ls -td ../masterdata_revert_* 2>/dev/null | head -n1))
                            ls -td ../masterdata_revert_* 2>/dev/null | while read dir; do
                                base=\$(basename "\$dir")
                                if [ "\$base" != "\$latest_revert" ]; then
                                    echo "\$SUDO_PASS" | sudo -S rm -rf "\$dir"
                                fi
                            done
                            cd ..
                        fi

                        if [ "${env.REVERT_UI}" = "true" ]; then
                            echo "🔄 Reverting UI..."
                            [ -d ${UI_FOLDER_NAME} ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_revert_\$TIMESTAMP || true
                            latest=\$(ls -td ${UI_FOLDER_NAME}_[0-9]* 2>/dev/null | head -n1)
                            if [ -n "\$latest" ] && [ -d "\$latest" ]; then
                                echo "🔁 Restoring: \$latest"
                                echo "\$SUDO_PASS" | sudo -S mv "\$latest" ${UI_FOLDER_NAME}
                            fi

                            echo "↩️ Restoring pdf folder from UI revert..."
                            [ -d ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME}_revert_\$TIMESTAMP/assets/pdf ${UI_FOLDER_NAME}/assets/ || true

                            cd ${UI_DEPLOY_PATH}
                            echo "\$SUDO_PASS" | sudo -S chmod -R 777 ${UI_FOLDER_NAME}

                            echo "🧹 Cleaning up old UI revert backups..."
                            latest_revert=\$(basename \$(ls -td ${UI_FOLDER_NAME}_revert_* 2>/dev/null | head -n1))
                            ls -td ${UI_FOLDER_NAME}_revert_* 2>/dev/null | while read dir; do
                                base=\$(basename "\$dir")
                                if [ "\$base" != "\$latest_revert" ]; then
                                    echo "\$SUDO_PASS" | sudo -S rm -rf "\$dir"
                                fi
                            done
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
                                echo "📦 Transferring UI zip..."
                                scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.ZIP_FILE_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                            """
                        }

                        if (env.USERMGMT_ZIP_NAME) {
                            sh """
                                echo "📦 Transferring USERMANAGEMENT zip..."
                                scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${DEST_TMP_PATH}/${env.USERMGMT_ZIP_NAME} ${REMOTE_USER}@${DEST_HOST}:${DEST_TMP_PATH}/
                            """
                        }

                        if (env.MASTERDATA_ZIP_NAME) {
                            sh """
                                echo "📦 Transferring MASTERDATA zip..."
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
                            echo "🚀 Starting UI Deployment..." 
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "📂 Extracting UI zip: ${env.ZIP_FILE_NAME}"
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.ZIP_FILE_NAME}

                                cd ${UI_DEPLOY_PATH}
                                echo "📁 Backing up current UI folder if exists"
                                [ -d ${UI_FOLDER_NAME} ] && echo "\$SUDO_PASS" | sudo -S mv ${UI_FOLDER_NAME} ${UI_FOLDER_NAME}_${timestamp} || echo "No existing UI to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/${UI_FOLDER_NAME} ${UI_DEPLOY_PATH}/
                                echo "📁 Backing up pdf folder if exists"
                                cd ${UI_DEPLOY_PATH}/${UI_FOLDER_NAME}/assets
                                [ -d pdf ] && echo "\$SUDO_PASS" | sudo -S mv pdf pdf_${timestamp} || echo "No pdf to backup"

                                echo "📁 Restoring folders from backup"
                                cd ${UI_DEPLOY_PATH}
                                BACKUP=${UI_FOLDER_NAME}_${timestamp}
                                if [ -d "\$BACKUP" ]; then
                                    [ -d "\$BACKUP/assets/pdf" ] && echo "\$SUDO_PASS" | sudo -S mv "\$BACKUP/assets/pdf" "${UI_FOLDER_NAME}/assets/" || true
                                    [ -d "\$BACKUP/usermanagement" ] && echo "\$SUDO_PASS" | sudo -S cp -r "\$BACKUP/usermanagement" "${UI_FOLDER_NAME}/" || true
                                    [ -d "\$BACKUP/masterdata" ] && echo "\$SUDO_PASS" | sudo -S cp -r "\$BACKUP/masterdata" "${UI_FOLDER_NAME}/" || true
                                fi

                                cd ${UI_DEPLOY_PATH}
                                echo "🧹 Cleaning up older UI backups"
                                #ls -td ${UI_FOLDER_NAME}_*/ | tail -n +3 | xargs -r echo "\$SUDO_PASS" | sudo -S rm -rf
                                ls -td ${UI_FOLDER_NAME}_* | grep -v '_revert_' | tail -n +3 | while read line; do echo "\$SUDO_PASS" | sudo -S rm -rf "\$line"; done
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
                            echo "🚀 Starting Usermanagement Deployment..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "📂 Extracting usermanagement zip: ${env.USERMGMT_ZIP_NAME}"
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.USERMGMT_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}${UI_FOLDER_NAME}
                                echo "📁 Backing up usermanagement folder if exists"
                                [ -d usermanagement ] && echo "\$SUDO_PASS" | sudo -S mv usermanagement ../usermanagement_${timestamp} || echo "No existing usermanagement to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/usermanagement ${UI_DEPLOY_PATH}${UI_FOLDER_NAME}/
                                echo "\$SUDO_PASS" | sudo -S cp -r ../usermanagement_${timestamp}/assets/user_files usermanagement/assets/ || true

                                echo "🧹 Cleaning up older usermanagement backups"
                                ls -td ../usermanagement_* | grep -v '_revert_' | tail -n +3 | while read line; do echo "\$SUDO_PASS" | sudo -S rm -rf "\$line"; done
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
                            echo "🚀 Starting Masterdata Deployment..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c '
                                export SUDO_PASS=${SUDO_PASS}
                                cd ${DEST_TMP_PATH}
                                echo "📂 Extracting masterdata zip: ${env.MASTERDATA_ZIP_NAME}"
                                echo "\$SUDO_PASS" | sudo -S unzip -o ${env.MASTERDATA_ZIP_NAME}

                                cd ${UI_DEPLOY_PATH}${UI_FOLDER_NAME}
                                echo "📁 Backing up masterdata folder if exists"
                                [ -d masterdata ] && echo "\$SUDO_PASS" | sudo -S mv masterdata ../masterdata_${timestamp} || echo "No existing masterdata to backup"
                                echo "\$SUDO_PASS" | sudo -S mv ${DEST_TMP_PATH}/masterdata ${UI_DEPLOY_PATH}${UI_FOLDER_NAME}/

                                echo "🧹 Cleaning up older masterdata backups"
                                ls -td ../masterdata_* | grep -v '_revert_' | tail -n +3 | while read line; do echo "\$SUDO_PASS" | sudo -S rm -rf "\$line"; done
                                echo "\$SUDO_PASS" | sudo -S chmod -R 777 masterdata
                            '
                        """
                    }
                }
            }
        }
    }
}
