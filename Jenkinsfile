pipeline { 
    agent { label 'master' }
    environment {
        KUBECONFIG = credentials('a700aafc-b29c-4052-a8f8-c93863709f25')
        PATH = "/usr/local/bin:$PATH"
    }    
    stages {
        stage('Setup') { 
            steps { 
                sh '''#!/bin/bash -ex
                    python3 -m venv scenario
                    source scenario/bin/activate
                    pip install --exists-action i yamllint
                    pip install --exists-action i flake8
                    pip install --exists-action i pytest
                    pip install .
                    oc version
                '''
            }
        }
        stage('Flake8') { 
            steps { 
                sh '''#!/bin/bash -ex
                    source scenario/bin/activate
                    find . -name *.py | grep -v 'doc' | xargs -i flake8 {}  --show-source --max-line-length=120
                '''
            }
        }         
        stage('PyTest') {
            steps { 
                sh '''#!/bin/bash -ex
                    source scenario/bin/activate
                    pytest -sv piqe_ocp_lib/tests
                '''
            }
        }
        stage('Cleanup') {
            steps {
                sh '''#!/bin/bash -ex
                    rm -rf scenario
                '''
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: '**/*', fingerprint: true
        }
    }
}
