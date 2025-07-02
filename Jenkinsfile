pipeline {
    agent any

    environment {
        FILES_LIST_FILE = "files_to_revert.txt"
        REMOTE_USER = "thahera"
        REMOTE_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        DEST_BASE_PATH = "/home/ubuntu/ACE-Camunda"
        SUDO_PASS = "1234"
    }

    stages {
        stage('Revert Files/Folders on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    script {
                        def fileList = readFile("${env.FILES_LIST_FILE}").split("\n")
                        for (rawLine in fileList) {
                            def FILE_PATH = rawLine.trim()
                            if (!FILE_PATH) continue

                            // Remove trailing slash
                            if (FILE_PATH.endsWith("/")) {
                                FILE_PATH = FILE_PATH[0..-2]
                            }

                            def DEST_PATH = "${env.DEST_BASE_PATH}/${FILE_PATH}"
                            def DEST_DIR = DEST_PATH.substring(0, DEST_PATH.lastIndexOf("/"))
                            def FILE_NAME = DEST_PATH.substring(DEST_PATH.lastIndexOf("/") + 1)
                            def TIMESTAMP = new Date().format("dd_MM_yy_HH_mm_ss")

                            echo "======== 🔄 Reverting: ${FILE_PATH} ========"

                            sh """
                                ssh -o StrictHostKeyChecking=no ${env.REMOTE_USER}@${env.REMOTE_HOST} bash -s <<'EOF'
                                set -e
                                cd "${DEST_DIR}"

                                echo "[🔍 Debug] Current dir: \$(pwd)"
                                echo "[🔍 Debug] Looking for: ${FILE_NAME}_*"

                                if [ -f "${FILE_NAME}" ]; then
                                    echo "🛡️ Backing up file as _rev_..."
                                    echo "${SUDO_PASS}" | sudo -S mv "${FILE_NAME}" "${FILE_NAME}_rev_${TIMESTAMP}"
                                elif [ -d "${FILE_NAME}" ]; then
                                    echo "🛡️ Backing up directory as _rev_..."
                                    echo "${SUDO_PASS}" | sudo -S mv "${FILE_NAME}" "${FILE_NAME}_rev_${TIMESTAMP}"
                                else
                                    echo "⚠️ ${FILE_NAME} does not exist, skipping _rev_ backup."
                                fi

                                echo "🔍 Looking for latest non-_rev_ backup..."
                                BACKUP=\$(ls -1td ${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | head -n1)

                                echo "[🔍 Debug] Found BACKUP = \$BACKUP"

                                if [ -n "\$BACKUP" ]; then
                                    echo "📦 Found backup: \$BACKUP"
                                    echo "🔁 Restoring \$BACKUP → ${FILE_NAME}"
                                    echo "${SUDO_PASS}" | sudo -S mv "\$BACKUP" "${FILE_NAME}"
                                else
                                    echo "⚠️ No valid backup found for ${FILE_NAME}"
                                fi

                                echo "🧹 Cleaning old _rev_ backups..."
                                #ls -1t ${FILE_NAME}_rev_* 2>/dev/null | tail -n +2 | xargs -r sudo rm -rf
                                find . -maxdepth 1 -name "${FILE_NAME}_rev_*" -printf "%T@ %p\n" 2>/dev/null | \
                                    sort -nr | tail -n +2 | cut -d' ' -f2- | xargs -r sudo rm -rf
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
                    sh """
                        echo "🔄 Restarting Docker containers (if needed)..."
                        ssh -o StrictHostKeyChecking=no ${env.REMOTE_USER}@${env.REMOTE_HOST} bash -c '
                            cd ${env.DEST_BASE_PATH}
                            # Uncomment below if needed:
                            # sudo docker-compose up --build -d --force-recreate
                        '
                    """
                }
            }
        }
    }
}
