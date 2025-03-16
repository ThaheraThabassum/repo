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
                        echo "Fetching latest changes..."
                        if [ -d "repo/.git" ]; then
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH}
                        else
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${TARGET_BRANCH}
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
                                # Rename original file to include _rev_ timestamp
                                mv "$item" "${item}_rev_${TIMESTAMP}"
                                echo "Renamed $item -> ${item}_rev_${TIMESTAMP}"

                                # Find latest backup (excluding _rev_ files)
                                LATEST_BACKUP=$(ls -t ${item}_* 2>/dev/null | grep -E "^${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}$" | head -n 1)

                                if [ -n "$LATEST_BACKUP" ] && [ -e "$LATEST_BACKUP" ]; then
                                    mv "$LATEST_BACKUP" "$item"
                                    echo "Restored $LATEST_BACKUP -> $item"
                                else
                                    echo "No valid backup found for $item"
                                fi
                            else
                                echo "$item not found, skipping."
                            fi
                        done < ${FILES_LIST_FILE}

                        git add .
                        git commit -m "Reverted files from backup"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
