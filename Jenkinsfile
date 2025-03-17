pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_revert.txt"
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
                            git checkout ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH}
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
                        git pull origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Reverting files/folders..."
                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                # Backup current file/folder before replacing it
                                BACKUP_ITEM="${item}_rev_${TIMESTAMP}"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"

                                # Find the latest backup specific to the item
                                LATEST_BACKUP=$(ls -td ${item}_* 2>/dev/null | grep -E "${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}" | grep -v "_rev_" | head -n 1)

                                if [ -n "$LATEST_BACKUP" ] && [ -e "$LATEST_BACKUP" ]; then
                                    echo "Restoring latest backup: $LATEST_BACKUP -> $item"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                else
                                    echo "No valid backup found for $item, skipping restore."
                                fi
                            else
                                echo "File/folder $item not found, skipping."
                            fi
                        done < ${FILES_LIST_FILE}

                        git commit -m "Reverted files based on ${FILES_LIST_FILE}"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
