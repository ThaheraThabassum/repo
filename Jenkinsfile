pipeline {
    agent any

    environment {
        SOURCE_REPO = 'git@github.com:ThaheraThabassum/repo.git'
        TARGET_REPO = 'git@github.com:ThaheraThabassum/testing.git'
        BRANCH = 'main'  // Change this if needed
        FILE_LIST = 'file_list.txt'  // The text file containing file/folder names
    }

    stages {
        stage('Checkout Source Repo') {
            steps {
                script {
                    sh """
                    rm -rf source-repo
                    git clone --depth=1 --branch $BRANCH $SOURCE_REPO source-repo
                    """
                }
            }
        }

        stage('Prepare Target Repo') {
            steps {
                script {
                    sh """
                    rm -rf target-repo
                    git clone --depth=1 $TARGET_REPO target-repo || exit 1
                    cd target-repo
                    
                    # Check if branch exists in remote
                    if ! git ls-remote --heads $TARGET_REPO $BRANCH | grep $BRANCH; then
                        echo "Branch $BRANCH does not exist in target repo. Creating..."
                        git checkout -b $BRANCH
                        git push origin $BRANCH
                    else
                        git checkout $BRANCH
                        git pull origin $BRANCH
                    fi
                    """
                }
            }
        }

        stage('Copy Specific Files/Folders') {
            steps {
                script {
                    sh """
                    cd source-repo
                    if [ ! -f $FILE_LIST ]; then
                        echo "Error: $FILE_LIST not found in the source repo!"
                        exit 1
                    fi

                    while IFS= read -r file; do
                        if [ -e "$file" ]; then
                            cp -r "$file" ../target-repo/
                        else
                            echo "Warning: $file not found in source repo!"
                        fi
                    done < $FILE_LIST
                    """
                }
            }
        }

        stage('Commit & Push to Target Repo') {
            steps {
                script {
                    sh """
                    cd target-repo
                    git add .
                    git commit -m 'Transferred specified files from repo to testing on branch $BRANCH' || echo "No changes to commit"
                    git push origin $BRANCH
                    """
                }
            }
        }
    }
}
