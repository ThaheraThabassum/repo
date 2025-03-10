pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_TO_COPY = "new_testing"
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

        stage('Backup Existing Files (If Present)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        
                        echo "Checking files for backup..."
                        for file in ${FILES_TO_COPY}; do
                            if [ -e "$file" ]; then
                                BACKUP_FILE="${file}_$TIMESTAMP"
                                mv "$file" "$BACKUP_FILE"
                                echo "Backup created: $BACKUP_FILE"
                                
                                git add "$BACKUP_FILE"
                                git commit -m "Backup created: $BACKUP_FILE"
                                git push origin ${TARGET_BRANCH}
                                
                                # Get the list of backup files and sort by timestamp in the filename
                                BACKUP_FILES=$(ls ${file}_* 2>/dev/null)
                                if [ -n "$BACKUP_FILES" ]; then
                                    SORTED_BACKUPS=$(echo "$BACKUP_FILES" | tr ' ' '\\n' | sort -t '_' -k 4n,4 -k 5n,5 -k 6n,6 -k 7n,7 -k 8n,8 | tr '\\n' ' ')
                                    BACKUP_COUNT=$(echo "$SORTED_BACKUPS" | wc -w)

                                    if [ "$BACKUP_COUNT" -gt 3 ]; then
                                        OLDEST_BACKUP=$(echo "$SORTED_BACKUPS" | awk '{print $1}')
                                        echo "Deleting oldest backup: $OLDEST_BACKUP"
                                        
                                        if [ -n "$OLDEST_BACKUP" ]; then
                                            rm -f "$OLDEST_BACKUP"
                                            git rm "$OLDEST_BACKUP"
                                            git commit -m "Removed oldest backup: $OLDEST_BACKUP"
                                            git push origin ${TARGET_BRANCH}
                                        fi
                                    fi
                                fi
                            else
                                echo "No existing file found for $file, skipping backup."
                            fi
                        done
                    '''
                }
            }
        }

        stage('Copy Files to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        
                        echo "Copying specific files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        git checkout ${SOURCE_BRANCH} -- ${FILES_TO_COPY}

                        echo "Setting permissions to 777 for copied files..."
                        chmod 777 ${FILES_TO_COPY}
                        
                        echo "Committing changes..."
                        git add ${FILES_TO_COPY}
                        git commit -m "Backup (if exists) & Copy: ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                        
                        echo "Pushing changes to ${TARGET_BRANCH}..."
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
