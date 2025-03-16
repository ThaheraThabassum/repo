pipeline {
    agent any

    environment {
        REPO_URL = 'git@github.com:ThaheraThabassum/repo.git'
        BRANCH_MAIN = 'main'
        BRANCH_AUTOMATE = 'automate'
        SSH_CREDENTIALS = 'git'
    }

    stages {
        stage('Checkout SCM') {
            steps {
                checkout([$class: 'GitSCM', 
                    branches: [[name: BRANCH_MAIN]], 
                    userRemoteConfigs: [[url: REPO_URL, credentialsId: SSH_CREDENTIALS]]
                ])
            }
        }

        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh '''
                        echo Checking if repository already exists...
                        [ -d repo/.git ] && echo "Repository exists. Fetching latest changes..." || git clone $REPO_URL repo
                        cd repo
                        git fetch --all
                        git reset --hard
                        git clean -fd
                        git checkout $BRANCH_MAIN
                        git pull origin $BRANCH_MAIN
                    '''
                }
            }
        }

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh '''
                        cd repo
                        git checkout $BRANCH_AUTOMATE
                        git pull origin $BRANCH_AUTOMATE
                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        for item in $(cat files_to_deploy.txt); do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM=${item}_${TIMESTAMP}
                                echo "Backing up $item -> $BACKUP_ITEM"
                                mv "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin $BRANCH_AUTOMATE
                            fi
                        done
                    '''
                }
            }
        }

        stage('Copy Files/Folders to Target Branch') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh '''
                        cd repo
                        git checkout $BRANCH_AUTOMATE
                        git reset --hard
                        echo "Copying specific files/folders from $BRANCH_MAIN to $BRANCH_AUTOMATE..."
                        for item in $(cat files_to_deploy.txt); do
                            git checkout $BRANCH_MAIN -- "$item"
                            chmod -R 777 "$item"
                            git add "$item"
                            git commit -m "Backup (if exists) & Copy: $item from $BRANCH_MAIN to $BRANCH_AUTOMATE"
                            git push origin $BRANCH_AUTOMATE
                        done
                    '''
                }
            }
        }

        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh '''
                        cd repo
                        git checkout $BRANCH_AUTOMATE
                        echo "Cleaning up old backups..."
                        for item in $(cat files_to_deploy.txt); do
                            BACKUP_ITEMS=$(ls -1t ${item}_* 2>/dev/null | tail -n +4)
                            if [ -n "$BACKUP_ITEMS" ]; then
                                echo "Removing old backups for $item..."
                                rm -rf $BACKUP_ITEMS
                                git rm -r $BACKUP_ITEMS
                                git commit -m "Removed old backups for $item"
                                git push origin $BRANCH_AUTOMATE
                            fi
                        done
                    '''
                }
            }
        }
    }
}
