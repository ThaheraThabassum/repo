pipeline {
    agent any
    
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        EXCEL_FILE = "files_to_deploy.xlsx"
        VENV_PATH = "venv"
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

        stage('Read Excel and Backup Existing Files') {
            steps {
                script {
                    echo "Setting up virtual environment and installing dependencies..."
                    sh '''
                        cd repo
                        if [ ! -d "${VENV_PATH}" ]; then
                            python3 -m venv ${VENV_PATH}
                        fi
                        source ${VENV_PATH}/bin/activate
                        pip install --upgrade pip
                        pip install pandas openpyxl
                    '''

                    echo "Extracting file list from Excel..."
                    sh '''
                        cd repo
                        source ${VENV_PATH}/bin/activate
                        python3 << EOPYTHON
import pandas as pd

excel_file = "${WORKSPACE}/${EXCEL_FILE}"
df = pd.read_excel(excel_file)

files = df['files'].dropna().tolist()

with open("files_to_deploy.txt", "w") as f:
    f.write("\\n".join(files))
EOPYTHON
                    '''

                    sshagent(credentials: [SSH_KEY]) {
                        sh '''
                            cd repo
                            git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                            git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."
                            git checkout ${SOURCE_BRANCH} -- files_to_deploy.txt

                            TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

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
                            done < files_to_deploy.txt
                        '''
                    }
                }
            }
        }

        stage('Deploy Files to Target Branch') {
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
                        done < files_to_deploy.txt
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
                                BACKUP_ITEMS=$(ls -1 ${BACKUP_PATTERN} 2>/dev/null | sort -r | tail -n +4)
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
                        done < files_to_deploy.txt
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'rm -rf venv'
        }
    }
}
