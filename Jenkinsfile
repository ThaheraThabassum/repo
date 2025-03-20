pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        XLSX_FILE = "files_to_deploy.xlsx"
        TXT_FILE = "files_to_deploy.txt"
    }
    stages {
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
                    sh 'python3 convert_xlsx.py'
                }
            }
        }

        stage('Prepare Repository') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        if [ -d "repo/.git" ]; then
                            cd repo
                            git fetch --all
                            git reset --hard
                            git clean -fd
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
                        else
                            git clone ${GIT_REPO} repo
                            cd repo
                            git checkout ${SOURCE_BRANCH}
                            git pull origin ${SOURCE_BRANCH}
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

                        if git ls-tree -r ${SOURCE_BRANCH} --name-only | grep -q "^${TXT_FILE}$"; then
                            git checkout ${SOURCE_BRANCH} -- ${TXT_FILE}
                        else
                            echo "Warning: ${TXT_FILE} not found in ${SOURCE_BRANCH}. Skipping backup."
                            exit 0
                        fi

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -e "$item" ]; then
                                BACKUP_ITEM="${item}_${TIMESTAMP}"
                                cp -r "$item" "$BACKUP_ITEM"
                                git add "$BACKUP_ITEM"
                                git commit -m "Backup created: $BACKUP_ITEM"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ${TXT_FILE}
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

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                git checkout ${SOURCE_BRANCH} -- "$item" 2>/dev/null || echo "File $item not found in ${SOURCE_BRANCH}, skipping."
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Copy: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            fi
                        done < ${TXT_FILE}
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

                        while IFS= read -r item || [ -n "$item" ]; do
                            if [ -n "$item" ]; then
                                BACKUP_PATTERN="${item}_*"
                                BACKUP_ITEMS=$(ls -d ${BACKUP_PATTERN} 2>/dev/null | sort -r | tail -n +4)
                                if [ -n "$BACKUP_ITEMS" ]; then
                                    echo "$BACKUP_ITEMS" | xargs rm -rf
                                    git rm -r $BACKUP_ITEMS 2>/dev/null
                                    git commit -m "Removed old backups, keeping only the latest 3"
                                    git push origin ${TARGET_BRANCH}
                                fi
                            fi
                        done < ${TXT_FILE}
                    '''
                }
            }
        }
    }
}
