pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        EXCEL_FILE = 'deploy_files.xlsx'
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

        stage('Read Files from Excel') {
            steps {
                script {
                    echo "Ensuring pip is installed..."
                    sh '''
                        python3 -m ensurepip || echo "pip is already installed"
                        python3 -m pip install --user openpyxl || echo "openpyxl already installed"
                    '''

                    echo "Reading deployment file names from ${EXCEL_FILE}..."

                    def files = sh(
                        script: '''
                        python3 - <<EOF
import openpyxl
import os

excel_path = os.path.join("repo", "${EXCEL_FILE}")
if not os.path.exists(excel_path):
    print(f"Error: {excel_path} not found")
    exit(1)

wb = openpyxl.load_workbook(excel_path)
sheet = wb.active

file_list = []
for row in sheet.iter_rows(values_only=True):
    if row and row[0]:  # Ensure row is not empty
        file_list.append(row[0].strip())

if not file_list:
    print("Error: No files found in Excel")
    exit(1)

print(" ".join(file_list))  # Output file names in a single line
EOF
                        ''',
                        returnStdout: true
                    ).trim()

                    if (files.isEmpty()) {
                        error "No files to process. Check the Excel file."
                    }

                    writeFile(file: 'file_list.txt', text: files)
                }
            }
        }

        stage('Backup Existing Files (If Present)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)
                        
                        echo "Checking files for backup..."
                        while IFS= read -r file; do
                            if [ -e "$file" ]; then
                                BACKUP_FILE="${file}_$TIMESTAMP"
                                mv "$file" "$BACKUP_FILE"
                                echo "Backup created: $BACKUP_FILE"
                                
                                git add "$BACKUP_FILE"
                                git commit -m "Backup created: $BACKUP_FILE"
                                git push origin ${TARGET_BRANCH}
                                
                                # Maintain only last 3 backups
                                BACKUP_FILES=$(ls ${file}_* 2>/dev/null)
                                if [ -n "$BACKUP_FILES" ]; then
                                    SORTED_BACKUPS=$(echo "$BACKUP_FILES" | tr ' ' '\\n' | sort | tr '\\n' ' ')
                                    BACKUP_COUNT=$(echo "$SORTED_BACKUPS" | wc -w)

                                    if [ "$BACKUP_COUNT" -gt 3 ]; then
                                        OLDEST_BACKUP=$(echo "$SORTED_BACKUPS" | awk '{print $1}')
                                        echo "Deleting oldest backup: $OLDEST_BACKUP"
                                        
                                        if [ -n "$OLDEST_BACKUP" ]; then
                                            rm -f "$OLDEST_BACKUP"
                                            git rm "$OLDEST_BACKUP"
                                            git commit -m "Removed oldest backup: $OLDEST_BACKUP"
                                            git push origin ${TARGET_BRANCH}
                                        fi
                                    fi
                                fi
                            else
                                echo "No existing file found for $file, skipping backup."
                            fi
                        done < ../file_list.txt
                    '''
                }
            }
        }

        stage('Copy Files to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH}
                        
                        echo "Copying specific files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}..."
                        while IFS= read -r file; do
                            git checkout ${SOURCE_BRANCH} -- "$file"
                        done < ../file_list.txt

                        echo "Setting permissions to 777 for copied files..."
                        chmod 777 $(cat ../file_list.txt)

                        echo "Committing changes..."
                        git add $(cat ../file_list.txt)
                        git commit -m "Backup (if exists) & Copy: Files from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                        
                        echo "Pushing changes to ${TARGET_BRANCH}..."
                        git push origin ${TARGET_BRANCH}
                    '''
                }
            }
        }
    }
}
