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
                    sh """
                        echo "Installing dependencies..."
                        pip3 install pandas openpyxl
                    """
                    script {
                        sh """
                            python3 << EOPYTHON
import pandas as pd
import datetime
import os
import subprocess

excel_file = "${env.FILES_LIST_FILE}"
df = pd.read_excel(excel_file)

timestamp = datetime.datetime.now().strftime("%d_%m_%y_%H_%M_%S")

for _, row in df.iterrows():
    file_path = str(row["files/folders path"]).strip()
    deploy = str(row["deploy_or_not"]).strip().lower()

    if deploy == "yes" and file_path:
        print(f"🔍 Processing backup for: {file_path}")

        if os.path.exists(file_path):
            if "." in file_path:
                filename, extension = os.path.splitext(file_path)
                backup_item = f"{filename}_{timestamp}{extension}"
            else:
                backup_item = f"{file_path}_{timestamp}"

            print(f"📦 Backing up {file_path} -> {backup_item}")
            subprocess.run(["cp", "-r", file_path, backup_item], check=True)

            subprocess.run(["git", "add", backup_item], check=True, cwd="repo")
            subprocess.run(["git", "commit", "-m", f"Backup created: {backup_item}"], check=True, cwd="repo")
            subprocess.run(["git", "push", "origin", "${env.TARGET_BRANCH}"], check=True, cwd="repo")
        else:
            print(f"⚠️ No existing file or folder found for {file_path}, skipping backup.")
EOPYTHON
                        """
                    }
                }
            }
        }

        stage('Copy Files/Folders to Target Branch') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Installing dependencies..."
                        pip3 install pandas openpyxl
                    """
                    script {
                        sh """
                            python3 << EOPYTHON
import pandas as pd
import os
import subprocess

excel_file = "${env.FILES_LIST_FILE}"
df = pd.read_excel(excel_file)

for _, row in df.iterrows():
    file_path = str(row["files/folders path"]).strip()
    deploy = str(row["deploy_or_not"]).strip().lower()

    if deploy == "yes" and file_path:
        print(f"🔍 Processing copy for: {file_path}")
        subprocess.run(["git", "checkout", "${env.SOURCE_BRANCH}", "--", file_path], check=True, cwd="repo")
        subprocess.run(["chmod", "-R", "777", file_path], check=True, cwd="repo")
        subprocess.run(["git", "add", file_path], check=True, cwd="repo")
        subprocess.run(["git", "commit", "-m", f"Backup (if exists) & Copy: {file_path} from ${env.SOURCE_BRANCH} to ${env.TARGET_BRANCH}"], check=True, cwd="repo")
        subprocess.run(["git", "push", "origin", "${env.TARGET_BRANCH}"], check=True, cwd="repo")
EOPYTHON
                        """
                    }
                }
            }
        }

        stage('Remove Old Backups (Keep Only 3)') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                        echo "Installing dependencies..."
                        pip3 install pandas openpyxl
                    """
                    script {
                        sh """
                            python3 << EOPYTHON
import pandas as pd
import os
import subprocess

excel_file = "${env.FILES_LIST_FILE}"
df = pd.read_excel(excel_file)

for _, row in df.iterrows():
    file_path = str(row["files/folders path"]).strip()
    deploy = str(row["deploy_or_not"]).strip().lower()

    if deploy == "yes" and file_path:
        print(f"🔍 Processing cleanup for: {file_path}")

        if "." in file_path:
            filename, extension = os.path.splitext(file_path)
            backup_pattern = f"{filename}_*"
        else:
            backup_pattern = f"{file_path}_*"

        backups = sorted([f for f in os.listdir(".") if f.startswith(backup_pattern)], key=lambda x: x.split("_")[-1])

        if len(backups) > 3:
            delete_count = len(backups) - 3
            delete_list = backups[:delete_count]

            for backup in delete_list:
                print(f"🗑️ Deleting old backup: {backup}")
                subprocess.run(["rm", "-rf", backup], check=True)
                subprocess.run(["git", "rm", "-r", backup], check=True, cwd="repo")

            subprocess.run(["git", "commit", "-m", "Removed old backups, keeping only the latest 3"], check=True, cwd="repo")
            subprocess.run(["git", "push", "origin", "${env.TARGET_BRANCH}"], check=True, cwd="repo")
        else:
            print("ℹ️ No old backups to delete.")
EOPYTHON
                        """
                    }
                }
            }
        }
    }
}
