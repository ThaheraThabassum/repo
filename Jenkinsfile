pipeline {
    agent any
    environment {
        // Source and Target Repo Details
        SOURCE_REPO = 'git@github.com:algonox/ACE-Camunda.git'
        SOURCE_BRANCH = 'kmb'
        TARGET_REPO = 'git@github.com:algonox/ACE-Camunda-DevOps.git'
        TARGET_BRANCH = 'kmb_uat'
        SSH_KEY = 'jenkins-ssh-key1'

        // File Handling
        FILES_TO_DEPLOY = "files_to_deploy.txt"
        FILES_TO_REVERT = "files_to_revert.txt"

        // Workspace
        SOURCE_REPO_DIR = 'kmb_local'
        TARGET_REPO_DIR = 'kmb_uat'
        WORKSPACE_DIR = "${WORKSPACE}"
    }

    stages {
        // Prepare Source Repository
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

        // Prepare Target Repository
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

        // Check if there are files to deploy
        stage('Check Deployment Files') {
            steps {
                script {
                    def deployFileExists = sh(script: "test -s ${WORKSPACE_DIR}/${FILES_TO_DEPLOY} && echo 'yes' || echo 'no'", returnStdout: true).trim()
                    env.SKIP_DEPLOY = (deployFileExists == 'no') ? "true" : "false"
                }
            }
        }

        // Backup Existing Files in Target Repo (only if deployment is needed)
        stage('Backup Existing Files in Target Repo') {
            when {
                expression { env.SKIP_DEPLOY != "true" }
            }
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        cp ${WORKSPACE_DIR}/${FILES_TO_DEPLOY} .

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                cp -rp "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                            fi
                        done < ${FILES_TO_DEPLOY}

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

        // Copy Files from Source to Target Repo (only if deployment is needed)
        stage('Copy Files from Source to Target Repo') {
            when {
                expression { env.SKIP_DEPLOY != "true" }
            }
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}

                        echo "${FILES_TO_DEPLOY}" >> .gitignore
                        git add .gitignore

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                cp -rp ../${SOURCE_REPO_DIR}/"$item" .
                                chmod -R 777 "$item"
                                git add -A
                            fi
                        done < ${FILES_TO_DEPLOY}

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

        // Remove Old Backups (Keep Only 3)
        stage('Remove Old Backups (Keep Only 3)') {
            when {
                expression { env.SKIP_DEPLOY != "true" }
            }
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
                        done < ${FILES_TO_DEPLOY}
                    '''
                }
            }
        }

        // Check if there are files to revert
        stage('Check Revert Files') {
            steps {
                script {
                    def revertFileExists = sh(script: "test -s ${WORKSPACE_DIR}/${FILES_TO_REVERT} && echo 'yes' || echo 'no'", returnStdout: true).trim()
                    env.SKIP_REVERT = (revertFileExists == 'no') ? "true" : "false"
                }
            }
        }

        // Revert Files/Folders (only if revert is needed)
        stage('Revert Files/Folders') {
            when {
                expression { env.SKIP_REVERT != "true" }
            }
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd ${TARGET_REPO_DIR}
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r item; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_rev_${TIMESTAMP}"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"

                                LATEST_BACKUP=$(ls -td ${item}_* | grep -E "${item}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}_[0-9]{2}" | grep -v "_rev_" | head -n 1)

                                if [ -n "$LATEST_BACKUP" ] && [ -e "$LATEST_BACKUP" ]; then
                                    mv "$LATEST_BACKUP" "$item"
                                    git add "$item"
                                fi
                            fi
                        done < ${FILES_TO_REVERT}

                        git commit -m "Reverted files based on ${FILES_TO_REVERT}"
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
