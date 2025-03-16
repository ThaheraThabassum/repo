pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_REVERT_LIST = "files_to_revert.txt"
    }
    stages {
        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Cloning repository..."
                        rm -rf repo
                        git clone ${GIT_REPO} repo
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        # Ensure latest files_to_revert.txt is available
                        git checkout ${TARGET_BRANCH} -- files_to_revert.txt
                    '''
                }
            }
        }

        stage('Revert Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Reverting files..."
                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                REV_FILE="${item}_rev_$TIMESTAMP"
                                echo "Backing up current file: $item -> $REV_FILE"
                                mv "$item" "$REV_FILE"
                                git add "$REV_FILE"
                                git commit -m "Backup before revert: $REV_FILE"
                                git push origin ${TARGET_BRANCH}

                                BACKUP_FILES=$(ls -t ${item}_* 2>/dev/null | grep -v "$REV_FILE" | head -1)
                                if [ -n "$BACKUP_FILES" ]; then
                                    LATEST_BACKUP=$(echo "$BACKUP_FILES" | head -1)
                                    echo "Restoring latest backup: $LATEST_BACKUP -> $item"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                    git commit -m "Reverted $item to latest backup: $LATEST_BACKUP"
                                    git push origin ${TARGET_BRANCH}
                                else
                                    echo "No backup found for $item, skipping restore."
                                fi
                            else
                                echo "File $item does not exist, skipping."
                            fi
                        done < ${FILES_REVERT_LIST}
                    '''
                }
            }
        }
    }
}
