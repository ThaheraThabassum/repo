pipeline {
    agent any
    environment {
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'
        UAT_SSH_KEY = 'jenkins-ssh-key1'
        UAT_SERVER = '65.1.176.9'
        FILES_LIST_FILE = "files_to_deploy.txt"
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}"
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
                            git reset --hard origin/${SOURCE_BRANCH}
                            git clean -fd
                        else
                            git clone ${SOURCE_REPO} ${SOURCE_REPO_DIR}
                        fi
                        cd ${SOURCE_REPO_DIR}
                        git checkout ${SOURCE_BRANCH}
                        git pull origin ${SOURCE_BRANCH}
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
                            git reset --hard origin/${TARGET_BRANCH}
                            git clean -fd
                        else
                            git clone ${TARGET_REPO} ${TARGET_REPO_DIR}
                        fi
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
        stage('Backup Existing Files/Folders in Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "Skipping backup: $item not found."
                            fi
                        done < ${WORKSPACE_DIR}/${FILES_LIST_FILE}
                    '''
                }
            }
        }
        stage('Copy Files/Folders from Source to Target Repo') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -e "../${SOURCE_REPO_DIR}/$item" ]; then
                                cp -r "../${SOURCE_REPO_DIR}/$item" .
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Copied: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "Skipping: $item does not exist in source repo."
                            fi
                        done < ${WORKSPACE_DIR}/${FILES_LIST_FILE}
                    '''
                }
            }
        }
        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        while IFS= read -r item || [ -n "$item" ]; do
                            BACKUP_PATTERN="${item}_*"
                            BACKUP_ITEMS=$(ls -d ${BACKUP_PATTERN} 2>/dev/null | sort -r | tail -n +4)
                            if [ -n "$BACKUP_ITEMS" ]; then
                                echo "$BACKUP_ITEMS" | xargs rm -rf
                                git rm -r $BACKUP_ITEMS 2>/dev/null
                                git commit -m "Removed old backups, keeping only the latest 3"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ${WORKSPACE_DIR}/${FILES_LIST_FILE}
                    '''
                }
            }
        }
        stage('Deploy to UAT') {
            steps {
                sshagent(credentials: [UAT_SSH_KEY]) {
                    sh '''
                        ssh -o StrictHostKeyChecking=no ${UAT_SERVER} << EOF
                        cd /home/ubuntu/ACE-Camunda
                        git pull origin ${TARGET_BRANCH}
                        sudo docker-compose up --build -d --force-recreate
                        EOF
                    '''
                }
            }
        }
    }
}
