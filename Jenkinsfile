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

        stage('Revert Items (Files/Folders)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Reverting items..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                filename="${item%.*}"
                                extension="${item##*.}"

                                if [ "$filename" = "$item" ]; then
                                    REVERT_ITEM="${filename}_rev_${TIMESTAMP}"
                                else
                                    REVERT_ITEM="${filename}_rev_${TIMESTAMP}.${extension}"
                                }

                                echo "Reverting $item -> $REVERT_ITEM"
                                mv "$item" "$REVERT_ITEM"
                                git add "$REVERT_ITEM"

                                # Find latest backup
                                if [ "$filename" = "$item" ]; then
                                    BACKUP_PATTERN="${filename}_*"
                                else
                                    BACKUP_PATTERN="${filename}_*.${extension}"
                                }

                                BACKUP_ITEMS=$(ls -1 ${BACKUP_PATTERN} 2>/dev/null | grep -v "_rev_" | sort -t '_' -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n)
                                LATEST_BACKUP=$(echo "$BACKUP_ITEMS" | tail -n 1)

                                if [ -n "$LATEST_BACKUP" ]; then
                                    echo "Latest backup found: $LATEST_BACKUP"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                    git rm "$REVERT_ITEM"
                                    git commit -m "Reverted $item from $LATEST_BACKUP"
                                    git push origin ${TARGET_BRANCH}
                                else
                                    echo "No backups found for $item."
                                    git commit -m "Reverted $item, no backup found."
                                    git push origin ${TARGET_BRANCH}
                                fi
                            else
                                echo "Item not found: $item"
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
    }
}
