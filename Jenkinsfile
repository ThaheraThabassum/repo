pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.txt"
    }
    stages {
        stage('Read Excel and Extract Paths') {
            steps {
                script {
                    def excelFile = 'input.xlsx' // Update with actual path
                    def extractedFiles = []
                    
                    // Read Excel file
                    def workbook = new org.apache.poi.xssf.usermodel.XSSFWorkbook(new FileInputStream(excelFile))
                    def sheet = workbook.getSheetAt(0) // Assuming first sheet
                    
                    sheet.each { row ->
                        def filePath = row.getCell(0)?.toString()?.trim()
                        def deployFlag = row.getCell(1)?.toString()?.trim()?.toLowerCase()
                        
                        if (filePath && deployFlag == 'yes') {
                            extractedFiles.add(filePath)
                        }
                    }
                    
                    workbook.close()
                    
                    // Write to FILES_LIST_FILE
                    new File(FILES_LIST_FILE).text = extractedFiles.join('\n')
                }
            }
        }
        
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

        stage('Backup and Deploy Files') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                        cd repo
                        git checkout ${TARGET_BRANCH} || git checkout -b ${TARGET_BRANCH}
                        git pull origin ${TARGET_BRANCH} || echo "Target branch not found. Creating it."
                        git checkout ${SOURCE_BRANCH} -- ${FILES_LIST_FILE}

                        TIMESTAMP=$(date +%d_%m_%y_%H_%M_%S)

                        echo "Processing files..."
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
                                
                                git checkout ${SOURCE_BRANCH} -- "$item"
                                chmod -R 777 "$item"
                                git add "$item"
                                git commit -m "Deployed: $item from ${SOURCE_BRANCH} to ${TARGET_BRANCH}"
                                git push origin ${TARGET_BRANCH}
                            else
                                echo "Skipping: No existing file or folder found for $item."
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
    }
}
