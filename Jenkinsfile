pipeline {
    agent any

    environment {
        FILES_LIST_FILE = "files_to_deploy.txt"
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        SOURCE_BASE_PATH = "/home/ubuntu/ACE-Camunda"
        DEST_BASE_PATH = "/home/ubuntu/ACE-Camunda-DevOps"
    }

    stages {
        stage('Server to Server Deployment') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    script {
                        def fileList = readFile(env.FILES_LIST_FILE).split("\n")
                        for (filePath in fileList) {
                            if (!filePath?.trim()) continue

                            // Handle Docker images separately
                            if (filePath.trim().startsWith("image:")) {
                                def imageName = filePath.trim().replace("image:", "").trim()
                                def sanitizedImage = imageName.replaceAll(/[/:]/, "_")

                                sh """#!/bin/bash
                                    set -e
                                    TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)
                                    IMAGE_TAR_NAME="${sanitizedImage}_local_\$TIMESTAMP.tar"
                                    BACKUP_TAR_NAME="${sanitizedImage}_UAT_bak_\$TIMESTAMP.tar"

                                    echo "Saving image on SOURCE_HOST as \$IMAGE_TAR_NAME..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} "cd /home/thahera && sudo docker save -o \$IMAGE_TAR_NAME ${imageName}"

                                    echo "Copying \$IMAGE_TAR_NAME to DEST_HOST..."
                                    scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:/home/thahera/\$IMAGE_TAR_NAME ${REMOTE_USER}@${DEST_HOST}:/home/thahera/

                                    echo "Backing up existing image on DEST_HOST as \$BACKUP_TAR_NAME..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd /home/thahera && sudo docker save -o \$BACKUP_TAR_NAME ${imageName} || echo 'Image not found for backup'"

                                    echo "Setting permissions for transferred image TAR..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "chmod 777 /home/${REMOTE_USER}/${TAR_FILE_NAME_LOCAL}"

                                    echo "Loading new image on DEST_HOST..."
                                    #ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd /home/thahera && sudo docker load -i \$IMAGE_TAR_NAME"
                                """
                                continue
                            }

                            // Normal file/folder deployment block
                            sh """#!/bin/bash
                                set -e
                                FILE_PATH='${filePath.trim()}'
                                TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)

                                if [[ \"\$FILE_PATH\" = /* ]]; then
                                    SRC_PATH=\"\$FILE_PATH\"
                                    DEST_PATH=\"\$FILE_PATH\"
                                else
                                    SRC_PATH=\"${SOURCE_BASE_PATH}/\$FILE_PATH\"
                                    DEST_PATH=\"${DEST_BASE_PATH}/\$FILE_PATH\"
                                fi

                                DEST_DIR=\$(dirname \"\$DEST_PATH\")
                                FILE_NAME=\$(basename \"\$DEST_PATH\")

                                echo "Checking if path is a directory on SOURCE_HOST..."
                                IS_DIR=\$(ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} "[ -d \"\$SRC_PATH\" ] && echo yes || echo no")

                                if [ \"\$IS_DIR\" = "yes" ]; then
                                    echo "Handling directory: \$SRC_PATH"
                                    TEMP_DIR="./temp_\${FILE_NAME}_\${TIMESTAMP}"
                                    mkdir -p \"\$TEMP_DIR\"

                                    echo "Copying directory from SOURCE_HOST to Jenkins workspace..."
                                    scp -r -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:\"\$SRC_PATH\" \"\$TEMP_DIR\"

                                    echo "Backing up existing directory on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "[ -d \"\$DEST_PATH\" ] && mv \"\$DEST_PATH\" \"\${DEST_DIR}/\${FILE_NAME}_\${TIMESTAMP}\" || echo 'No existing directory to backup.'"

                                    echo "Creating destination directory on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p \"\$DEST_DIR\""

                                    echo "Transferring directory from Jenkins workspace to DEST_HOST..."
                                    scp -r -o StrictHostKeyChecking=no \"\$TEMP_DIR/\$(basename \"\$SRC_PATH\")\" ${REMOTE_USER}@${DEST_HOST}:\"\$DEST_DIR/\"

                                    echo "Setting permissions for transferred directory..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod -R 777 \"\$DEST_PATH\""

                                    echo "Cleaning up temp directory locally..."
                                    rm -rf \"\$TEMP_DIR\"

                                    echo "Cleaning up old backups for directory on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd \"\$DEST_DIR\" && ls -dt \${FILE_NAME}_*/ 2>/dev/null | tail -n +4 | xargs -r rm -rf"

                                else
                                    TEMP_FILE="./temp_\$FILE_NAME"

                                    echo "Creating destination directory on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p \"\$DEST_DIR\""

                                    echo "Backing up existing file if present on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "if [ -f \"\$DEST_PATH\" ]; then cp -p \"\$DEST_PATH\" \"\$DEST_PATH\"_\$TIMESTAMP; fi"

                                    echo "Copying file from SOURCE_HOST to Jenkins workspace..."
                                    scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:\"\$SRC_PATH\" \"\$TEMP_FILE\"

                                    echo "Transferring file from Jenkins workspace to DEST_HOST..."
                                    scp -o StrictHostKeyChecking=no \"\$TEMP_FILE\" ${REMOTE_USER}@${DEST_HOST}:\"\$DEST_PATH\"

                                    echo "Setting 777 permission on DEST_HOST for transferred file..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod 777 \"\$DEST_PATH\""

                                    echo "Cleaning up temp file locally..."
                                    rm -f \"\$TEMP_FILE\"

                                    echo "Cleaning up old file backups..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "cd \"\$DEST_DIR\" && ls -t \${FILE_NAME}_* 2>/dev/null | tail -n +4 | xargs -r rm -f"
                                fi
                            """
                        }
                    }
                }
            }
        }

        stage('Restart Docker on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Stopping all running Docker containers on DEST_HOST..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c "'
                            CONTAINERS=\$(sudo docker ps -aq)
                            if [ -n \"\$CONTAINERS\" ]; then
                                echo \"Stopping containers...\"
                                sudo docker stop \$CONTAINERS
                                echo \"Removing containers...\"
                                sudo docker rm \$CONTAINERS
                            else
                                echo \"No running containers to stop/remove.\"
                            fi
                            echo \"Recreating containers with docker-compose...\"
                            cd ${DEST_BASE_PATH}
                            sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
