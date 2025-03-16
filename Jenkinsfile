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
                            # Handle directories
                            if [ -d "$item" ]; then
                                BACKUP_DIRS=$(ls -d ${item}_* 2>/dev/null | grep -E "^${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}$")
                                if [ -n "$BACKUP_DIRS" ]; then
                                    SORTED_BACKUPS=$(echo "$BACKUP_DIRS" | tr ' ' '\\n' | sort -t '_' -k 3n,3 -k 2n,2 -k 1n,1 -k 4n,4 -k 5n,5 -k 6n,6 | tr '\\n' ' ')
                                    BACKUP_COUNT=$(echo "$SORTED_BACKUPS" | wc -w)

                                    if [ "$BACKUP_COUNT" -gt 3 ]; then
                                        OLDEST_BACKUP=$(echo "$SORTED_BACKUPS" | awk '{print $1}')
                                        echo "Deleting oldest backup directory: $OLDEST_BACKUP"
                                        rm -rf "$OLDEST_BACKUP"
                                        git rm -r "$OLDEST_BACKUP"
                                        git commit -m "Removed oldest backup directory: $OLDEST_BACKUP"
                                        git push origin ${TARGET_BRANCH}
                                    fi
                                }
                            # Handle files
                            elif [ -f "$item" ]; then
                                BACKUP_FILES=$(ls -d ${item}_* 2>/dev/null | grep -E "^${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}$")
                                if [ -n "$BACKUP_FILES" ]; then
                                    SORTED_BACKUPS=$(echo "$BACKUP_FILES" | tr ' ' '\\n' | sort -t '_' -k 3n,3 -k 2n,2 -k 1n,1 -k 4n,4 -k 5n,5 -k 6n,6 | tr '\\n' ' ')
                                    BACKUP_COUNT=$(echo "$SORTED_BACKUPS" | wc -w)

                                    if [ "$BACKUP_COUNT" -gt 3 ]; then
                                        OLDEST_BACKUP=$(echo "$SORTED_BACKUPS" | awk '{print $1}')
                                        echo "Deleting oldest backup file: $OLDEST_BACKUP"
                                        rm -rf "$OLDEST_BACKUP"
                                        git rm -r "$OLDEST_BACKUP"
                                        git commit -m "Removed oldest backup file: $OLDEST_BACKUP"
                                        git push origin ${TARGET_BRANCH}
                                    fi
                                }
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
    }
}
