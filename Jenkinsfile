pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_revert.txt"
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
                            git remote set-url origin ${GIT_REPO} # Correct remote URL
                            git fetch --all
                            git reset --hard origin/${TARGET_BRANCH}
                            git clean -fd
                            git checkout ${TARGET_BRANCH}
                            git pull --rebase=false origin ${TARGET_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${TARGET_BRANCH}
                            git pull --rebase=false origin ${TARGET_BRANCH}
                        fi
                    '''
                }
            }
        }

        stage('Revert Files/Folders') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull --rebase=false origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Reverting files/folders..."
                        cp ${WORKSPACE_DIR}/${FILES_LIST_FILE} .

                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_rev_${TIMESTAMP}"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"

                                LATEST_BACKUP=$(ls -td ${item}_* 2>/dev/null | grep -E "${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}" | grep -v "_rev_" | sort -r | head -n 1)

                                if [ -n "$LATEST_BACKUP" ] && [ -e "$LATEST_BACKUP" ]; then
                                    echo "Restoring latest backup: $LATEST_BACKUP -> $item"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                else
                                    echo "No valid backup found for $item, skipping restore."
                                fi

                                echo "Cleaning up old _rev_ backups for $item..."
                                OLD_BACKUPS=$(ls -td ${item}_rev_* 2>/dev/null | tail -n +3)
                                if [ -n "$OLD_BACKUPS" ]; then
                                    echo "Deleting old backups: $OLD_BACKUPS"
                                    rm -rf $OLD_BACKUPS
                                    git rm -r $OLD_BACKUPS
                                fi

                            else
                                echo "File/folder $item not found, skipping."
                            fi
                        done < ${FILES_LIST_FILE}

                        git commit -m "Reverted files based on ${FILES_LIST_FILE} and cleaned old backups"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
