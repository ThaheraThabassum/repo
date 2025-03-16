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

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Creating backups..."
                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_$TIMESTAMP"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                            else
                                echo "No existing file or folder found for $item, skipping backup."
                            fi
                        done < ${FILES_LIST_FILE}

                        git commit -m "Backup created before update"
                        git push origin ${TARGET_BRANCH}
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
                            git checkout ${SOURCE_BRANCH} -- "$item" || echo "Warning: $item not found in source branch"
                            chmod -R 777 "$item"
                            git add "$item"
                        done < ${FILES_LIST_FILE}

                        git commit -m "Updated files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}" || echo "No changes to commit"
                        git push origin ${TARGET_BRANCH}
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
                            BACKUP_ITEMS=$(ls -1tr ${item}_* 2>/dev/null | head -n -3)

                            if [ -n "$BACKUP_ITEMS" ]; then
                                echo "Deleting oldest backups: $BACKUP_ITEMS"
                                rm -rf $BACKUP_ITEMS
                                git rm -r $BACKUP_ITEMS || echo "Warning: Some files were already deleted"
                            else
                                echo "No old backups found for $item"
                            fi
                        done < ${FILES_LIST_FILE}

                        git commit -m "Removed old backups" || echo "No old backups to delete"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
