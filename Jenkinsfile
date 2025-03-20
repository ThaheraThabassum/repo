pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
        EXCEL_FILE = "files_to_deploy.xlsx"
        PYTHON_VENV = "venv"
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
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            echo "Cloning repository..."
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        fi
                    '''
                }
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                script {
                    sh '''
                        echo "Creating Python virtual environment..."
                        python3 -m venv ${PYTHON_VENV}
                        source ${PYTHON_VENV}/bin/activate
                        pip install --upgrade pip
                        pip install pandas numpy openpyxl
                    '''
                }
            }
        }

        stage('Extract Deployment List from Excel') {
            steps {
                script {
                    sh '''
                        echo "Extracting deployment list from Excel..."
                        source ${PYTHON_VENV}/bin/activate

                        python3 - <<EOF
import pandas as pd
import numpy as np

df = pd.read_excel("${EXCEL_FILE}", engine='openpyxl')
deploy_files = df[df['deploy_or_not'].str.lower() == 'yes']['file/folders path'].dropna()

deploy_files.to_csv("${FILES_LIST_FILE}", index=False, header=False)

print("Deployment list generated: ${FILES_LIST_FILE}")
EOF
                    '''
                }
            }
        }

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."
                        git checkout ${SOURCE_BRANCH} -- ${FILES_LIST_FILE}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Creating backups..."
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
                                echo "No existing file or folder found for $item, skipping backup."
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Copy Files/Folders to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}

                        echo "Copying specific files/folders from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                git checkout ${SOURCE_BRANCH} -- "$item"
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Backup (if exists) & Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ${FILES_LIST_FILE}
                    '''
                }
            }
        }

        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        echo "Cleaning up old backups..."
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

        stage('Cleanup Python Virtual Environment') {
            steps {
                sh '''
                    echo "Cleaning up virtual environment..."
                    rm -rf ${PYTHON_VENV}
                '''
            }
        }
    }
}
