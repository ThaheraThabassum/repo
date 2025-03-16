pipeline {
    agent any

    environment {
        SOURCE_BRANCH = "main"
        TARGET_BRANCH = "automate"
        FILES_LIST_FILE = "files_to_deploy.txt"
        TIMESTAMP = new Date().format("dd_MM_yy_HH_mm_ss")
    }

    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(['git']) {
                    sh '''
                        echo "Checking if repository already exists..."
                        if [ -d repo/.git ]; then
                            echo "Repository exists. Fetching latest changes..."
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone git@github.com:ThaheraThabassum/repo.git repo
                            cd repo
                            git checkout ${SOURCE_BRANCH}
                        fi
                    '''
                }
            }
        }

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(['git']) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        echo "Creating backups..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                filename="${item%.*}"
                                extension="${item##*.}"

                                if [ "$filename" == "$extension" ]; then
                                    BACKUP_ITEM="${item}_${TIMESTAMP}"
                                else
                                    BACKUP_ITEM="${filename}_${TIMESTAMP}.${extension}"
                                fi

                                echo "Backing up $item -> $BACKUP_ITEM"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            elif [ -z "$item" ]; then
                                echo "Skipping empty line in ${FILES_LIST_FILE}"
                            else
                                echo "No existing file or folder found for $item, skipping backup."
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Copy Files/Folders to Target Branch') {
            steps {
                sshagent(['git']) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}

                        echo "Copying specific files/folders from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                git checkout ${SOURCE_BRANCH} -- "$item"
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Backup (if exists) & Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "Skipping empty line in ${FILES_LIST_FILE}"
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(['git']) {
                    sh '''
                        cd repo
                        echo "Removing old backups, keeping only the last 3..."

                        for dir in $(cat ${FILES_LIST_FILE}); do
                            ls -t ${dir}_* 2>/dev/null | tail -n +4 | xargs rm -f
                        done

                        git add .
                        git commit -m "Removed old backups, keeping only last 3"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }

    post {
        failure {
            echo 'Pipeline failed! Please check the logs for details.'
        }
        success {
            echo 'Pipeline executed successfully!'
        }
    }
}
