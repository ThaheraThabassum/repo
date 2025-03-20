pipeline {
    agent any
    environment {
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}" // Capture the workspace directory
    }
    stages {
        stage('Prepare Source Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Cloning or fetching source repository..."
                        if [ -d "${SOURCE_REPO_DIR}/.git" ]; then
                            cd ${SOURCE_REPO_DIR}
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            git clone ${SOURCE_REPO} ${SOURCE_REPO_DIR}
                            cd ${SOURCE_REPO_DIR}
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        fi
                    '''
                }
            }
        }
        stage('Prepare Target Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Cloning or fetching target repository..."
                        if [ -d "${TARGET_REPO_DIR}/.git" ]; then
                            cd ${TARGET_REPO_DIR}
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH}
                        else
                            git clone ${TARGET_REPO} ${TARGET_REPO_DIR}
                            cd ${TARGET_REPO_DIR}
                            git checkout ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH}
                        fi
                    '''
                }
            }
        }
        stage('Backup Existing Files/Folders in Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                        cp ${WORKSPACE_DIR}/${FILES_LIST_FILE} .

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        echo "Creating backups in target repo..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                if [[ "$item" == *.* ]]; then
                                    filename="${item%.*}"
                                    extension="${item##*.}"
                                    BACKUP_ITEM="${filename}_${TIMESTAMP}.${extension}"
                                else
                                    BACKUP_ITEM="${item}_${TIMESTAMP}"
                                fi
                                echo "Backing up $item -> $BACKUP_ITEM"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "No existing file or folder found for $item in target repo, skipping backup."
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
        stage('Copy Files/Folders from Source to Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        echo "Copying specific files/folders from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                cp -r ../${SOURCE_REPO_DIR}/"$item" .
                                chmod -R 777 "$item" 
                                git add "$item"
                                git commit -m "Copied: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
        stage('Remove Old Backups (Keep Only 3) in Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        echo "Cleaning up old backups in target repo..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                echo "Checking backups for $item..."
                                if [[ "$item" == *.* ]]; then
                                    filename="${item%.*}"
                                    extension="${item##*.}"
                                    BACKUP_PATTERN="${filename}_*"
                                else
                                    BACKUP_PATTERN="${item}_*"
                                fi
                                BACKUP_ITEMS=$(ls -d ${BACKUP_PATTERN} 2>/dev/null | sort -t '_' -k 2,2n -k 3,3n -k 4,4n -k 5,5n -k 6,6n)
                                echo "Found backups: $BACKUP_ITEMS"
                                BACKUP_COUNT=$(echo "$BACKUP_ITEMS" | wc -w)
                                if [ "$BACKUP_COUNT" -gt 3 ]; then
                                    DELETE_COUNT=$((BACKUP_COUNT - 3))
                                    echo "Deleting $DELETE_COUNT old backups..."
                                    echo "$BACKUP_ITEMS" | head -n "$DELETE_COUNT" | xargs rm -rf
                                    git rm -r $(echo "$BACKUP_ITEMS" | head -n "$DELETE_COUNT") 2>/dev/null
                                    git commit -m "Removed old backups, keeping only the latest 3"
                                    git push origin ${TARGET_BRANCH}
                                else
                                    echo "No old backups to delete."
                                fi
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }
    }
}
