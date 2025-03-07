pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'  // Source branch
        TARGET_BRANCH = 'automate'  // Target branch
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_TO_COPY = "new_testing"
    }
    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Checking repository..."
                    if [ -d "repo/.git" ]; then
                        cd repo
                        git fetch --all
                        git reset --hard
                        git clean -fd
                        git checkout ${SOURCE_BRANCH}
                        git pull origin ${SOURCE_BRANCH}
                    else
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
                            
                            # Keep only the latest 3 backups
                            BACKUP_FILES=$(ls -tr ${file}_* 2>/dev/null | head -n -3)
                            if [ -n "$BACKUP_FILES" ]; then
                                echo "Deleting old backups..."
                                echo "$BACKUP_FILES" | xargs rm -f
                                echo "$BACKUP_FILES" | xargs git rm
                                git commit -m "Removed old backups for $file"
                                git push origin ${TARGET_BRANCH}
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
                    
                    echo "Committing changes..."
                    git add ${FILES_TO_COPY}
                    git commit -m "Backup & Copy: ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                    
                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
