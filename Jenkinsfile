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
                    sh '''
                        set -e
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r FILE_PATH || [ -n "$FILE_PATH" ]; do
                            [ -z "$FILE_PATH" ] && continue

                            if echo "$FILE_PATH" | grep -q "^/"; then
                                SRC_PATH="$FILE_PATH"
                                DEST_PATH="$FILE_PATH"
                            else
                                SRC_PATH="${SOURCE_BASE_PATH}/$FILE_PATH"
                                DEST_PATH="${DEST_BASE_PATH}/$FILE_PATH"
                            fi

                            DEST_DIR=$(dirname "$DEST_PATH")
                            FILE_NAME=$(basename "$DEST_PATH")

                            echo "Creating destination directory on DEST_HOST..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "mkdir -p $DEST_DIR"

                            echo "Backing up existing file if present on DEST_HOST..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "
                                if [ -f $DEST_PATH ]; then
                                    cp -p $DEST_PATH ${DEST_PATH}_$TIMESTAMP
                                fi
                            "

                            echo "Copying file from SOURCE_HOST to Jenkins workspace..."
                            scp -o StrictHostKeyChecking=no ${REMOTE_USER}@${SOURCE_HOST}:$SRC_PATH ./temp_$FILE_NAME

                            echo "Transferring file from Jenkins workspace to DEST_HOST..."
                            scp -o StrictHostKeyChecking=no ./temp_$FILE_NAME ${REMOTE_USER}@${DEST_HOST}:$DEST_PATH

                            echo "Cleaning up temp file locally..."
                            rm -f ./temp_$FILE_NAME

                            echo "Cleaning up old backups on DEST_HOST..."
                            ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} "
                                cd $DEST_DIR
                                ls -t ${FILE_NAME}_* 2>/dev/null | tail -n +4 | xargs -r rm -f
                            "

                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Restart Docker on Destination') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${DEST_HOST} << 'EOF'
                            echo "Restarting Docker containers (if needed)..."
                            cd ${DEST_BASE_PATH}
                            # Uncomment if needed:
                            # docker-compose down && docker-compose up -d
                        EOF
                    """
                }
            }
        }
    }
}
