pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_XLSX = "files_to_deploy.xlsx"
        WORKSPACE_DIR = "${WORKSPACE}"
    }
    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Checking if repository already exists..."
                        if [ -d "repo/.git" ]; then
                            echo "Repository exists. Fetching latest changes..."
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        fi
                    '''
                }
            }
        }

        stage('Read File List from XLSX') {
            steps {
                script {
                    def fileList = readXlsx file: "${WORKSPACE_DIR}/${FILES_LIST_XLSX}", sheetName: 'Sheet1', cellRange: 'A2:A100'
                    env.FILES_TO_DEPLOY = fileList.collect { it[0] }.join('\n')
                }
            }
        }

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Creating backups..."
                        echo "${FILES_TO_DEPLOY}" | while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                if [[ "$item" == *.* ]]; then
                                    filename="${item%.*}"
                                    extension="${item##*.}"
                                    BACKUP_ITEM="${filename}_${TIMESTAMP}.${extension}"
                                else
                                    BACKUP_ITEM="${item}_${TIMESTAMP}"
                                fi

                                echo "Backing up $item -> $BACKUP_ITEM"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "No existing file or folder found for $item, skipping backup."
                            fi
                        done
                    '''
                }
            }
        }

        stage('Copy Files/Folders to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}

                        echo "Copying specific files/folders from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        echo "${FILES_TO_DEPLOY}" | while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                git checkout ${SOURCE_BRANCH} -- "$item"
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Backup (if exists) & Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done
                    '''
                }
            }
        }

        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        echo "Cleaning up old backups..."
                        echo "${FILES_TO_DEPLOY}" | while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                echo "Checking backups for $item..."
                                if [[ "$item" == *.* ]]; then
                                    filename="${item%.*}"
                                    extension="${item##*.}"
                                    BACKUP_PATTERN="${filename}_*"
                                else
                                    BACKUP_PATTERN="${item}_*"
                                fi

                                BACKUP_ITEMS=$(ls -d ${BACKUP_PATTERN} 2>/dev/null | sort -t '_' -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n)

                                echo "Found backups: $BACKUP_ITEMS"
                                BACKUP_COUNT=$(echo "$BACKUP_ITEMS" | wc -w)

                                if [ "$BACKUP_COUNT" -gt 3 ]; then
                                    DELETE_COUNT=$((BACKUP_COUNT - 3))
                                    echo "Deleting $DELETE_COUNT old backups..."

                                    echo "$BACKUP_ITEMS" | head -n "$DELETE_COUNT" | xargs rm -rf
                                    git rm -r $(echo "$BACKUP_ITEMS" | head -n "$DELETE_COUNT") 2>/dev/null
                                    git commit -m "Removed old backups, keeping only the latest 3"
                                    git push origin ${TARGET_BRANCH}
                                else
                                    echo "No old backups to delete."
                                fi
                            fi
                        done
                    '''
                }
            }
        }
    }
}
