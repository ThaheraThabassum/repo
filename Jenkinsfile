pipeline {
    agent any
    environment {
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_DEPLOY_LIST_FILE = "files_to_deploy.txt"
        FILES_REVERT_LIST_FILE = "files_to_revert.txt"
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}"
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
        stage('Deploy Files (if list not empty)') {
            when {
                expression {
                    fileExists(path: "${FILES_DEPLOY_LIST_FILE}") && readFile(file: "${FILES_DEPLOY_LIST_FILE}").trim() != ''
                }
            }
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        cp ${WORKSPACE_DIR}/${FILES_DEPLOY_LIST_FILE} .

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                cp -rp "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                            fi
                        done < ${FILES_DEPLOY_LIST_FILE}

                        if git diff --cached --quiet; then
                            echo "No changes to commit in backup."
                        else
                            git commit -m "Backup created on $TIMESTAMP"
                            git push origin ${TARGET_BRANCH}
                        fi

                        echo "${FILES_DEPLOY_LIST_FILE}" >> .gitignore
                        git add .gitignore

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                cp -rp ../${SOURCE_REPO_DIR}/"$item" .
                                chmod -R 777 "$item"
                                git add -A
                            fi
                        done < ${FILES_DEPLOY_LIST_FILE}

                        if git diff --cached --quiet; then
                            echo "No changes to commit in file copy."
                        else
                            git commit -m "Copied files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                            git push origin ${TARGET_BRANCH}
                        fi

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
                        done < ${FILES_DEPLOY_LIST_FILE}
                    '''
                }
            }
        }
        stage('Revert Files (if list not empty)') {
            when {
                expression {
                    fileExists(path: "${FILES_REVERT_LIST_FILE}") && readFile(file: "${FILES_REVERT_LIST_FILE}").trim() != ''
                }
            }
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull --rebase=false origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Reverting files/folders..."
                        cp ${WORKSPACE_DIR}/${FILES_REVERT_LIST_FILE} .

                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_rev_${TIMESTAMP}"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"

                                LATEST_BACKUP=$(ls -td ${item}_* | grep -E "${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}" | grep -v "_rev_" | head -n 1)

                                if [ -n "$LATEST_BACKUP" ] && [ -e "$LATEST_BACKUP" ]; then
                                    echo "Restoring latest backup: $LATEST_BACKUP -> $item"
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                else
                                    echo "No valid backup found for $item, skipping restore."
                                fi

                                echo "Cleaning up old _rev_ backups for $item..."
                                OLD_BACKUPS=$(ls -td ${item}_rev_* | tail -n +3)
                                if [ -n "$OLD_BACKUPS" ]; then
                                    echo "Deleting old backups: $OLD_BACKUPS"
                                    rm -rf $OLD_BACKUPS
                                    git rm -r $OLD_BACKUPS
                                fi
                            else
                                echo "File/folder $item not found, skipping."
                            fi
                        done < ${FILES_REVERT_LIST_FILE}

                        git commit -m "Reverted files based on ${FILES_REVERT_LIST_FILE} and cleaned old backups"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
