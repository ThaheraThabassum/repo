pipeline {
    agent any

    environment {
        FILES_LIST_FILE = "files_to_deploy.txt"
        REMOTE_USER = "thahera"
        SOURCE_HOST = "3.111.252.210"
        DEST_HOST = "65.1.176.9"
        SSH_KEY = "08cc52e2-f8f2-4479-87eb-f8307f8d23a8"
        SOURCE_BASE_PATH = "/home/ubuntu/ACE-Camunda"
        DEST_BASE_PATH = "/home/ubuntu/ACE-Camunda"
        IMAGE_WORK_DIR = "/home/thahera"
        CUSTOM_EXTRACTION_SOURCE = "/var/www/extraction_folder"
        CUSTOM_EXTRACTION_DEST = "/opt" 
    }

    stages {
        stage('Server to Server Deployment') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    script {
                        def fileList = readFile(env.FILES_LIST_FILE).split("\n")
                        for (line in fileList) {
                            def filePath = line.trim()
                            if (!filePath) continue

                            echo "======================================="
                            echo " Processing: ${filePath}"
                            echo "======================================="

                            // New functionality for extraction_folder
                            if (filePath == "extraction_folder") {
                                def folderName = env.CUSTOM_EXTRACTION_SOURCE.tokenize("/").last()
                                def timestamp = new Date().format("dd_MM_yy_HH_mm_ss")

                                sh """
                                    set -e
                                    TEMP_DIR="./temp_extraction_\${folderName}_\${timestamp}"
                                    mkdir -p "\$TEMP_DIR"

                                    echo "📥 Copying extraction folder from SOURCE_HOST..."
                                    scp -r -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:"${CUSTOM_EXTRACTION_SOURCE}" "\$TEMP_DIR"

                                    echo "🛡️ Backing up existing folder on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "[ -d '${CUSTOM_EXTRACTION_DEST}' ] && mv '${CUSTOM_EXTRACTION_DEST}' '${CUSTOM_EXTRACTION_DEST}_\${timestamp}' || echo 'No folder to backup.'"

                                    echo "📁 Creating destination path on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p '${CUSTOM_EXTRACTION_DEST}'"

                                    echo "🚀 Transferring extracted folder to DEST_HOST..."
                                    scp -r -o StrictHostKeyChecking=no "\$TEMP_DIR/${folderName}" ${REMOTE_USER}@${DEST_HOST}:"\${CUSTOM_EXTRACTION_DEST}/"

                                    echo "🔒 Setting permissions..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "sudo chmod -R 777 '${CUSTOM_EXTRACTION_DEST}/${folderName}'"

                                    echo "🧹 Cleaning temp directory..."
                                    rm -rf "\$TEMP_DIR"
                                """
                                continue
                            }

                            // Existing Docker image handling
                            if (filePath.startsWith("image:")) {
                                def imageName = filePath.replace("image:", "").trim()
                                def imageBase = imageName.tokenize("/").last().replaceAll("[:/]", "_")
                                def timestamp = new Date().format("dd_MM_yy_HH_mm_ss")
                                def imageTar = "${imageBase}_local_${timestamp}.tar"
                                def imageTarBak = "${imageBase}_uat_bak_${timestamp}.tar"

                                sh """
                                    echo "🧹 Cleaning up old .tar files on SOURCE_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && rm -f ${imageBase}_local_*.tar || echo 'No old tars to clean.'"

                                    echo "Saving image on SOURCE_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && echo '1234' | sudo -S docker save -o ${imageTar} ${imageName}"

                                    echo "Setting permissions on image tar..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && echo '1234' | sudo -S chmod 777 ${imageTar}"

                                    echo " Cleaning up .tar on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && rm -f ${imageBase}_local_*.tar"

                                    echo "Transferring image tar to DEST_HOST..."
                                    scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:${IMAGE_WORK_DIR}/${imageTar} \
                                        ${REMOTE_USER}@${DEST_HOST}:${IMAGE_WORK_DIR}/

                                    echo " Cleaning up .tar on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && rm -f ${imageBase}_uat_bak_*.tar"

                                    echo " 🛡️Backing up existing Docker image on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && echo '1234' | sudo -S docker save -o ${imageTarBak} ${imageName} || echo 'No existing image to backup.'"

                                    echo "🔒 Setting permissions on backup and new image tar..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && echo '1234' | sudo -S chmod 777 ${imageTar} ${imageTarBak}"

                                    echo "✅ Loading Docker image on DEST_HOST..."
                                    #ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        #"cd ${IMAGE_WORK_DIR} && echo '1234' | sudo -S docker load -i ${imageTar}"

                                    echo " Cleaning up .tar on DEST_HOST..."
                                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                        "cd ${IMAGE_WORK_DIR} && rm -f ${imageBase}_local_*.tar"
                                """
                            } else {
                                // Existing file/folder logic
                                def trimmedPath = filePath
                                sh """
                                    set -e
                                    FILE_PATH='${trimmedPath}'
                                    TIMESTAMP=\$(date +%d_%m_%y_%H_%M_%S)

                                    if [[ "\$FILE_PATH" = /* ]]; then
                                        SRC_PATH="\$FILE_PATH"
                                        DEST_PATH="\$FILE_PATH"
                                    else
                                        SRC_PATH="${SOURCE_BASE_PATH}/\$FILE_PATH"
                                        DEST_PATH="${DEST_BASE_PATH}/\$FILE_PATH"
                                    fi

                                    DEST_DIR=\$(dirname "\$DEST_PATH")
                                    FILE_NAME=\$(basename "\$DEST_PATH")

                                    echo "Checking if path is a directory on SOURCE_HOST..."
                                    IS_DIR=\$(ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST} \
                                        "[ -d \"\$SRC_PATH\" ] && echo yes || echo no")

                                    if [ "\$IS_DIR" = "yes" ]; then
                                        echo "Handling directory: \$SRC_PATH"
                                        TEMP_DIR="./temp_\${FILE_NAME}_\${TIMESTAMP}"
                                        mkdir -p "\$TEMP_DIR"

                                        echo "Copying directory from SOURCE_HOST to Jenkins workspace..."
                                        scp -r -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:"\$SRC_PATH" "\$TEMP_DIR"

                                        echo "🛡️Backing up existing directory on DEST_HOST..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                            "[ -d \"\$DEST_PATH\" ] && mv \"\$DEST_PATH\" \"\${DEST_DIR}/\${FILE_NAME}_\${TIMESTAMP}\" || echo 'No existing dir to backup.'"

                                        echo "Creating destination directory on DEST_HOST..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p \"\$DEST_DIR\""

                                        echo "Transferring directory..."
                                        scp -r -o StrictHostKeyChecking=no "\$TEMP_DIR/\$(basename \"\$SRC_PATH\")" ${REMOTE_USER}@${DEST_HOST}:"\$DEST_DIR/"

                                        echo "🔒 Setting permissions for transferred directory..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod -R 777 \"\$DEST_PATH\""

                                        rm -rf "\$TEMP_DIR"

                                        echo "Cleaning up old backups for directory on DEST_HOST..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                            "cd \"\$DEST_DIR\" && ls -dt \${FILE_NAME}_*/ 2>/dev/null | grep -v '_rev_' | tail -n +4 | xargs -r rm -rf"
                                    else
                                        TEMP_FILE="./temp_\$FILE_NAME"
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p \"\$DEST_DIR\""

                                        echo "🛡️Backing up existing directory on DEST_HOST..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                            "[ -f \"\$DEST_PATH\" ] && cp -p \"\$DEST_PATH\" \"\$DEST_PATH\"_\$TIMESTAMP || echo 'No file to backup.'"

                                        scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:"\$SRC_PATH" "\$TEMP_FILE"
                                        scp -o StrictHostKeyChecking=no "\$TEMP_FILE" ${REMOTE_USER}@${DEST_HOST}:"\$DEST_PATH"

                                        echo "🔒 Setting permissions for transferred file..."
                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "sudo chmod 777 \"\$DEST_PATH\""
                                        rm -f "\$TEMP_FILE"

                                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} \
                                            "cd \"\$DEST_DIR\" && ls -t \${FILE_NAME}_* 2>/dev/null | grep -v '_rev_' | tail -n +4 | xargs -r rm -f"
                                    fi
                                """
                            }
                        }
                    }
                }
            }
        }

        stage('Restart Docker on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "==============================="
                        echo "🔄 Restarting Docker containers on DEST_HOST"
                        echo "==============================="

                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} bash -c "'
                            CONTAINERS=\$(sudo docker ps -aq)
                            if [ -n \"\$CONTAINERS\" ]; then
                                echo \"Stopping containers...\"
                                #sudo docker stop \$CONTAINERS
                                echo \"Removing containers...\"
                                #sudo docker rm \$CONTAINERS
                            else
                                echo \"No running containers to stop/remove.\"
                            fi
                            echo \"Recreating containers with docker-compose...\"
                            cd ${DEST_BASE_PATH}
                            #sudo docker-compose up --build -d --force-recreate
                        '"
                    '''
                }
            }
        }
    }
}
