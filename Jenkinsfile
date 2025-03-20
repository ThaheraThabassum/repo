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
                        echo "Checking if repository exists..."
                        if [ -d "repo/.git" ]; then
                            echo "Repository found. Fetching latest changes..."
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
                        fi
                    '''
                }
            }
        }

        stage('Setup Python Virtual Environment') {
            steps {
                sh '''
                    echo "Setting up Python virtual environment..."
                    sudo apt-get install -y python3-venv || echo "Skipping package install (no sudo)"
                    python3 -m venv ${PYTHON_VENV} && source ${PYTHON_VENV}/bin/activate && \
                    pip install --upgrade pip && pip install pandas numpy openpyxl
                '''
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
df = pd.read_excel("${EXCEL_FILE}", engine='openpyxl')
deploy_files = df[df['deploy_or_not'].str.lower() == 'yes']['file/folders path'].dropna()

deploy_files.to_csv("${FILES_LIST_FILE}", index=False, header=False)
print(f"Deployment list saved: {FILES_LIST_FILE}")
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
                        git checkout ${SOURCE_BRANCH} -- ${FILES_LIST_FILE} || echo "No file list to checkout."

                        TIMESTAMP=$(date +%Y%m%d_%H%M%S)
                        echo "Creating backups..."

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "Skipping non-existent: $item"
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

                        echo "Copying files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                git checkout ${SOURCE_BRANCH} -- "$item"
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

        stage('Remove Old Backups (Keep 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH}

                        echo "Cleaning old backups..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                BACKUP_PATTERN="${item}_*"
                                BACKUP_ITEMS=$(find . -name "${BACKUP_PATTERN}" | sort | head -n -3)

                                if [ -n "$BACKUP_ITEMS" ]; then
                                    echo "Deleting: $BACKUP_ITEMS"
                                    rm -rf $BACKUP_ITEMS
                                    git rm -r $BACKUP_ITEMS 2>/dev/null || true
                                    git commit -m "Removed old backups, kept latest 3"
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
                    echo "Cleaning virtual environment..."
                    rm -rf ${PYTHON_VENV}
                '''
            }
        }
    }
}
