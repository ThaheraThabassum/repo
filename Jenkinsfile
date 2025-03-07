pipeline {
    agent any
    environment {
        SSH_KEY = '08cc52e2-f8f2-4479-87eb-f8307f8d23a8' // Replace with your correct Jenkins SSH credential ID
        REMOTE_USER = 'thahera'     // Replace with your remote server username
        REMOTE_HOST = '3.111.252.210' // Replace with your remote server IP/hostname
    }
    stages {
        stage('Check SSH Connection and Set Permissions') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh """
                    echo "Attempting to connect to ${REMOTE_HOST}..."
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} <<'EOF'
                    echo "Successfully logged in!"
                    cd /home/ubuntu/
                    sudo chmod 777 testing_jenkinsfile.txt
                    cat testing_jenkinsfile.txt
                    logout
                    EOF
                    """
                }
            }
        }
    }
}
