pipeline {
    agent any
    environment {
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
        REVERT_FILES_LIST = "files_to_revert.txt"
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}"
    }
    stages {
        stage('Check if Deployment is Needed') {
            steps {
                script {
                    if (fileExists(FILES_LIST_FILE)) {
                        def deployFiles = readFile(FILES_LIST_FILE).trim()
                        if (deployFiles == '') {
                            echo "No files to deploy, skipping deployment steps."
                            return
                        }
                    }
                }
            }
        }
        
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

                                # Keep only the latest 3 backups
                                BACKUP_ITEMS=$(ls -t ${item}_* 2>/dev/null | tail -n +4)
                                if [ -n "$BACKUP_ITEMS" ]; then
                                    echo "Deleting old backups..."
                                    echo "$BACKUP_ITEMS" | xargs rm -rf
                                    echo "$BACKUP_ITEMS" | xargs git rm -r --ignore-unmatch
                                fi
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
                        echo "Copying files from source repo to target repo..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                cp -rp ../${SOURCE_REPO_DIR}/"$item" .
                                chmod -R 777 "$item"
                                git add "$item"
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
        
        stage('Revert Process if Required') {
            steps {
                script {
                    if (fileExists(REVERT_FILES_LIST)) {
                        def revertFiles = readFile(REVERT_FILES_LIST).trim()
                        if (revertFiles == '') {
                            echo "No files to revert, skipping revert process."
                            return
                        }
                    }
                }
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}
                        if [ ! -s "${WORKSPACE_DIR}/${REVERT_FILES_LIST}" ]; then
                            echo "No files to revert. Exiting."
                            exit 0
                        fi
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                                mv "$item" "${item}_rev_$TIMESTAMP"
                                LATEST_BACKUP=$(ls -t ${item}_* 2>/dev/null | head -n 1)
                                if [ -n "$LATEST_BACKUP" ]; then
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                    echo "Reverted $item to latest backup."
                                else
                                    echo "No backup found for $item."
                                fi
                            fi
                        done < ${WORKSPACE_DIR}/${REVERT_FILES_LIST}
                        if git diff --cached --quiet; then
                            echo "No changes to commit."
                        else
                            git commit -m "Reverted files as per ${REVERT_FILES_LIST}"
                            git push origin ${TARGET_BRANCH}
                        fi
                    '''
                }
            }
        }
    }
}
