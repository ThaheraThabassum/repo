pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        XLSX_FILE = "files_to_deploy.xlsx"
        TXT_FILE = "files_to_deploy.txt"
        VENV_DIR = 'venv'
    }

    stages {
        stage('Setup Python Environment') {
            steps {
                script {
                    sh '''
                        echo "Checking and installing python3-venv if not available..."
                        if ! python3 -m ensurepip --version >/dev/null 2>&1; then
                            echo "Installing python3-venv..."
                            sudo apt update && sudo apt install -y python3-venv
                        fi

                        echo "Creating Python virtual environment..."
                        python3 -m venv ${VENV_DIR}
                        source ${VENV_DIR}/bin/activate
                        pip install --upgrade pip
                        pip install pandas openpyxl
                        deactivate
                    '''
                }
            }
        }

        stage('Convert XLSX to TXT') {
            steps {
                script {
                    def pythonScript = '''
import pandas as pd

xlsx_file = "files_to_deploy.xlsx"
txt_file = "files_to_deploy.txt"

try:
    df = pd.read_excel(xlsx_file, header=None)
    df.to_csv(txt_file, index=False, header=False)
    print(f"Converted {xlsx_file} to {txt_file} successfully.")
except Exception as e:
    print(f"Error: {str(e)}")
    exit(1)
'''
                    writeFile file: 'convert_xlsx.py', text: pythonScript
                    sh '''
                        source ${VENV_DIR}/bin/activate
                        python3 convert_xlsx.py
                        deactivate
                    '''
                }
            }
        }

        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        echo "Checking if repository exists..."
                        if [ -d "repo/.git" ]; then
                            echo "Repository exists. Resetting state..."
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
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

        stage('Backup Existing Files/Folders') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Creating backups..."
                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ] && [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                echo "Backing up $item -> $BACKUP_ITEM"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "No existing file or folder found for $item, skipping backup."
                            fi
                        done < ../${TXT_FILE}
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
                                git commit -m "Backup & Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ../${TXT_FILE}
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
                                BACKUP_PATTERN="${item}_*"
                                BACKUP_ITEMS=$(ls -d ${BACKUP_PATTERN} 2>/dev/null | sort | tail -n +4)

                                if [ -n "$BACKUP_ITEMS" ]; then
                                    echo "Deleting old backups..."
                                    echo "$BACKUP_ITEMS" | xargs rm -rf
                                    git rm -r $(echo "$BACKUP_ITEMS") 2>/dev/null
                                    git commit -m "Removed old backups, keeping only the latest 3"
                                    git push origin ${TARGET_BRANCH}
                                else
                                    echo "No old backups to delete."
                                fi
                            fi
                        done < ../${TXT_FILE}
                    '''
                }
            }
        }
    }
}
