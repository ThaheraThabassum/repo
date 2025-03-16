pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
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

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."
                        git checkout ${SOURCE_BRANCH} -- ${FILES_LIST_FILE}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Creating backups..."
                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_$TIMESTAMP"
                                echo "Backing up $item -> $BACKUP_ITEM"

                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
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
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}

                        echo "Copying specific files/folders from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r item; do
                            git checkout ${SOURCE_BRANCH} -- "$item"
                            chmod -R 777 "$item"

                            git add "$item"
                            git commit -m "Backup (if exists) & Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                            git push origin ${TARGET_BRANCH}
                        done < ${FILES_LIST_FILE}
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

                        echo "Cleaning up old backups..."
                        while IFS= read -r item; do
                            BACKUP_ITEMS=$(ls -1t ${item}_*)
                            BACKUP_TO_DELETE=$(ls -1t ${item}_* | tail -n +$(($(ls -1t ${item}_* | wc -l) - 3)))

                            if [ -n "$BACKUP_TO_DELETE" ]; then
                                echo "Deleting oldest backups: $BACKUP_TO_DELETE"
                                echo "$BACKUP_TO_DELETE" | xargs rm -rf
                                echo "$BACKUP_TO_DELETE" | xargs git rm -rf
                                git commit -m "Removed oldest backups: $BACKUP_TO_DELETE"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "No old backups found for $item"
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
    }
}
