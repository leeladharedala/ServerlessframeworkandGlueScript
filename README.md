This project deploys an AWS Glue ETL job using the Serverless Framework. 
It provisions an S3 bucket for data storage, an IAM role for permissions, and a Glue job to process large-scale transaction sequences efficiently with PySpark.

Project Structure
├── serverless.yml              
├── resources/
│   ├── s3-bucket.yml            # Defines the S3 bucket for Glue job storage
│   ├── iam-role.yml             # Defines IAM role and permissions
│   ├── glue-job.yml             # Defines AWS Glue ETL job
├── GlueScripts/
│   ├── generate_users.py        # Generates and stores fake user data in S3
│   ├── generate_transactions.py # Generates transactions for users
│   ├── generate_sequences.py    # Generates sequences per transaction
└── dependencies/                # Required Python dependencies


Prerequisites

•	Install Serverless Framework:

 npm install -g serverless

•	Install required plugins:

npm install --save-dev serverless-s3-sync

•	Configure AWS credentials:

aws configure


Deployment to AWS:

serverless deploy

Remove Deployment:

serverless remove


Workflow
1.	Generate Users (generate_users.py)
Creates fake user profiles and stores them in S3.

3.	Generate Transactions (generate_transactions.py)
Reads users from S3 and generates transactions per user.

4.	Generate Sequences (generate_sequences.py)
Reads transactions from S3 and creates multiple sequences per transaction.
