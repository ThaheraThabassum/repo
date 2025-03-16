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

        stage('Revert Files/Folders from Backup') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                echo "Backing up current file: $item -> ${item}_rev_${TIMESTAMP}"
                                mv "$item" "${item}_rev_${TIMESTAMP}"
                                git add "${item}_rev_${TIMESTAMP}"
                            
                                echo "Finding the latest backup for $item..."
                                LATEST_BACKUP=$(ls -1 "${item}_"* 2>/dev/null | grep -E "${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}" | sort -t '_' -k 3,3n -k 2,2n -k 1,1n -k 4,4n -k 5,5n -k 6,6n | tail -n 1)
                            
                                if [ -n "$LATEST_BACKUP" ]; then
                                    echo "Restoring latest backup: $LATEST_BACKUP -> $item"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                else
                                    echo "No backup found for $item, skipping restore."
                                fi
                            fi
                        done < ${FILES_REVERT_LIST}

                        git commit -m "Reverted files from backup"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
