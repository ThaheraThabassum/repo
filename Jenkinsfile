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
        stage('Revert Files/Folders on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    script {
                        def lines = readFile(env.FILES_LIST_FILE).split("\n")
                        for (rawLine in lines) {
                            def filePath = rawLine.trim()
                            if (!filePath) continue

                            // Remove trailing slash if it's a folder
                            if (filePath.endsWith("/")) {
                                filePath = filePath[0..-2]
                            }

                            def timestamp = new Date().format("dd_MM_yy_HH_mm_ss")
                            def destPath = "${DEST_BASE_PATH}/${filePath}"
                            def destDir = destPath.substring(0, destPath.lastIndexOf("/"))
                            def fileName = destPath.substring(destPath.lastIndexOf("/") + 1)

                            echo "======== 🔄 Reverting: ${filePath} ========"

                            sh """
                                ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} 'bash -s' <<'EOF'
                                set -e
                                cd "${destDir}"

                                if [ -f "${fileName}" ]; then
                                    echo "🛡️ Backing up file as _rev_..."
                                    echo "1234" | sudo -S mv "${fileName}" "${fileName}_rev_${timestamp}"
                                elif [ -d "${fileName}" ]; then
                                    echo "🛡️ Backing up directory as _rev_..."
                                    echo "1234" | sudo -S mv "${fileName}" "${fileName}_rev_${timestamp}"
                                else
                                    echo "⚠️ \${fileName} does not exist, skipping _rev_ backup."
                                fi

                                echo "🔍 Looking for latest non-_rev_ backup..."
                                BACKUP=\$(ls -1td \${fileName}_* 2>/dev/null | grep -v '_rev_' | head -n1)

                                if [ -n "\$BACKUP" ]; then
                                    echo "📦 Found backup: \$BACKUP"
                                    echo "🔁 Restoring \$BACKUP → \${fileName}"
                                    echo "1234" | sudo -S mv "\$BACKUP" "\${fileName}"
                                else
                                    echo "⚠️ No valid backup found for \${fileName}"
                                fi

                                echo "🧹 Cleaning old _rev_ backups..."
                                ls -1t \${fileName}_rev_* 2>/dev/null | tail -n +2 | xargs -r sudo rm -rf
                                EOF
                            """
                        }
                    }
                }
            }
        }

        stage('Restart Docker (optional)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "🔄 Restarting Docker containers on DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} bash -c "cd ${DEST_BASE_PATH} && echo 'Recreate if needed'"
                        # sudo docker-compose up --build -d --force-recreate
                    '''
                }
            }
        }
    }
}
