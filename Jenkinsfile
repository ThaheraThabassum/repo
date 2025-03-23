pipeline {
    agent any
    environment {
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'  // For repo access
        UAT_SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8'  // For UAT SSH connection
        FILES_LIST_FILE = "files_to_deploy.txt"
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}"
        REMOTE_USER = 'thahera'         // Change to UAT SSH username
        REMOTE_HOST = '65.1.176.9' // Change to UAT server IP
    }
    stages {
        stage('Prepare Source Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Cloning or updating source repo..."
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
                        echo "Cloning or updating target repo..."
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
        stage('Backup Existing Files in Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        cp ${WORKSPACE_DIR}/${FILES_LIST_FILE} .

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                cp -rp "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                            fi
                        done < ${FILES_LIST_FILE}

                        if git diff --cached --quiet; then
                            echo "No changes to commit in backup."
                        else
                            git commit -m "Backup created on $TIMESTAMP"
                            git push origin ${TARGET_BRANCH}
                        fi
                    '''
                }
            }
        }
        stage('Copy Files from Source to Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}

                        echo "${FILES_LIST_FILE}" >> .gitignore
                        git add .gitignore

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                cp -rp ../${SOURCE_REPO_DIR}/"$item" .
                                chmod -R 777 "$item"
                                git add -A
                            fi
                        done < ${FILES_LIST_FILE}

                        if git diff --cached --quiet; then
                            echo "No changes to commit in file copy."
                        else
                            git commit -m "Copied files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                            git push origin ${TARGET_BRANCH}
                        fi
                    '''
                }
            }
        }
        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                echo "Checking backups for $item..."
                                BACKUP_ITEMS=$(find . -maxdepth 1 -name "${item}_*" | sort | head -n -3)

                                if [ -n "$BACKUP_ITEMS" ]; then
                                    echo "Deleting old backups..."
                                    echo "$BACKUP_ITEMS" | xargs rm -rf
                                    echo "$BACKUP_ITEMS" | xargs git rm -r --ignore-unmatch
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
        stage('Connect to UAT Server via SSH') {
            steps {
                sshagent(credentials: [UAT_SSH_KEY]) {
                    sh '''
                        echo "Connecting to UAT server ${REMOTE_HOST}..."
                        ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} << "EOF"
                            echo "Successfully connected to ${REMOTE_HOST}"
                            cd /home/ubuntu/ACE-Camunda/
                            echo "Pulling latest changes from Git..."
                            sudo git pull 
                            echo "Restarting Docker containers..."
                            sudo docker-compose up --build -d --force-recreate
                            echo "Deployment completed."
                        EOF
                    '''
                }
            }
        }
    }
}
