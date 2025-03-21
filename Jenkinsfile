pipeline {
    agent any
    environment {
        GIT_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'automate'
        SSH_KEY = 'jenkins-ssh-key1'
        FILES_LIST_FILE = "files_to_deploy.xlsx"
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
                        python3 -c 'import openpyxl, os; try: wb = openpyxl.load_workbook("${FILES_LIST_FILE}"); sheet = wb.active; for row in sheet.iter_rows(min_row=1): item = row[0].value; if item and item.strip(): if os.path.exists(item): filename, ext = os.path.splitext(item); backup_item = f"{filename}_{os.environ["TIMESTAMP"]}{ext}" if ext else f"{item}_{os.environ["TIMESTAMP"]}"; print(f"Backing up {item} -> {backup_item}"); os.system(f"cp -r \\"{item}\\" \\"{backup_item}\\"; git add \\"{backup_item}\\"; "); else: print(f"No existing file or folder found for {item}, skipping backup."); except Exception as e: print(f"Error during backup: {e}")'

                        git commit -m "Backup created: $(date +%d_%m_%y_%H_%M_%S)"
                        git push origin ${TARGET_BRANCH}
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
                        python3 -c 'import openpyxl, os; try: wb = openpyxl.load_workbook("${FILES_LIST_FILE}"); sheet = wb.active; for row in sheet.iter_rows(min_row=1): item = row[0].value; if item and item.strip(): os.system(f"git checkout ${os.environ["SOURCE_BRANCH"]} -- \\"{item}\\"; chmod -R 777 \\"{item}\\"; git add \\"{item}\\"; git commit -m \\"Backup (if exists) & Copy: {item} from ${os.environ["SOURCE_BRANCH"]} to ${os.environ["TARGET_BRANCH"]}\\"") ; except Exception as e: print(f"Error during copy: {e}")'
                        git push origin ${TARGET_BRANCH}
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
                        python3 -c 'import openpyxl, os, subprocess; try: wb = openpyxl.load_workbook("${FILES_LIST_FILE}"); sheet = wb.active; for row in sheet.iter_rows(min_row=1): item = row[0].value; if item and item.strip(): filename, ext = os.path.splitext(item); backup_pattern = f"{filename}_*" if ext else f"{item}_*"; backups = subprocess.check_output(["ls", "-d", backup_pattern], text=True, stderr=subprocess.DEVNULL, shell=True).splitlines(); if backups: backups.sort(key=lambda x: [int(part) if part.isdigit() else part for part in x.split("_")]); backup_count = len(backups); if backup_count > 3: delete_count = backup_count - 3; to_delete = backups[:delete_count]; print(f"Deleting {delete_count} old backups..."); for backup in to_delete: os.system(f"rm -rf \\"{backup}\\"; git rm -r \\"{backup}\\"; git commit -m \\"Removed old backups, keeping only the latest 3\\""); os.system(f"git push origin ${os.environ["TARGET_BRANCH"]}") else: print("No old backups to delete."); else: print(f"No backups found for {item}"); except Exception as e: print(f"Error during backup cleanup: {e}")'
                    '''
                }
            }
        }
    }
}
