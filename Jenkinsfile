

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
        // ... (Prepare Repository stage remains the same)

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

                                # Get the total count of backup files
                                BACKUP_COUNT=$(ls -tr ${file}_* 2>/dev/null | wc -l)

                                # Only delete if there are more than 3 backups
                                if [ "$BACKUP_COUNT" -gt 3 ]; then
                                    # Correction: Use 'tail -n +4' to select the oldest backups
                                    BACKUP_FILES=$(ls -tr ${file}_* 2>/dev/null | head -n $(($BACKUP_COUNT-3))) #selecting old backups
                                    echo "Deleting old backups: $BACKUP_FILES"
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
                    git commit -m "Backup (if exists) & Copy: ${FILES_TO_COPY} from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                    
                    echo "Pushing changes to ${TARGET_BRANCH}..."
                    git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
