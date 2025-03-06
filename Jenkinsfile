pipeline {
    agent any
    environment {
        SSH_KEY = 'jenkins-ssh-key'  // Replace with your correct Jenkins SSH credential ID
        REMOTE_USER = 'thahera'     // Replace with your remote server username
        REMOTE_HOST = '43.204.7.124' // Replace with your remote server IP/hostname
    }
    stages {
        stage('Check SSH Connection') {
            steps {
                sshagent(credentials: [SSH_KEY]) {
                    sh '''
                    echo "Attempting to connect to ${REMOTE_HOST}..."
                    ssh -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "echo 'Successfully logged in!'"
                    '''
                }
            }
        }
    }
}
