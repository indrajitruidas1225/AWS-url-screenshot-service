# URL Screenshot Service on AWS EC2

This is a simple but comprehensive hands-on project to help you get familiar with key features of **Amazon EC2**, including:

- Working with **multiple EC2 instances**
- Using **SQS (Simple Queue Service)** for asynchronous communication
- Running **Node.js** and **Python** in different environments
- Uploading files to **S3**
- Assigning **IAM roles** to EC2 instances securely

---

## Project Overview

The project architecture is as follows:

1. A **Node.js server** (on one EC2 instance) receives a URL via API and pushes it to an **SQS queue**.
2. A separate **Python worker** (on another EC2 instance) pulls messages from the queue, takes a screenshot of the URL using **Playwright**, and uploads the screenshot to **Amazon S3**.
3. The uploaded screenshot becomes publicly accessible (using a bucket policy).

---

## Prerequisites

- An AWS account
- S3 bucket (e.g., `screenshot-bucket-indra`)
- An SQS queue (e.g., `url-queue`)
- Two EC2 instances (Amazon Linux or Ubuntu 22.04)
- A security group that allows:
  - SSH (port 22)
  - HTTP (port 3000) for the Node.js server

---

## Setup Steps

---

### 1. Launch EC2 Instances

Create **two separate EC2 instances** from the AWS console:

- **App Server (Node.js)**: Handles incoming requests
- **Worker (Python)**: Consumes SQS messages and processes them

Select Ubuntu 22.04 or Amazon Linux 2 (Free Tier eligible).

While launching:

- Assign a proper **IAM Role** to each instance with access to:
  - SQS (send and receive)
  - S3 (upload objects)
- Ensure both instances are in the same **VPC/Subnet** for simplicity

---

### 2. SSH Into Instances

From your local machine:

```bash
# For App server
ssh -i your-key.pem ubuntu@<App_Instance_Public_IP>

# For Worker
ssh -i your-key.pem ubuntu@<Worker_Instance_Public_IP>
````

Replace `your-key.pem` with your EC2 key pair and IPs with the public IPv4 of each instance.

---

### 3. Install Node.js (App Server)

On the **App instance**:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
node -v
npm -v
```

Then install dependencies:

```bash
npm install aws-sdk express body-parser
```

---

### 4. Install Python + Playwright (Worker)

On the **Worker instance**:

```bash
sudo apt update
sudo apt install -y python3-pip
pip install boto3 playwright

# Install system dependencies for browser automation
sudo playwright install-deps

# Install browser engines (Chromium, Firefox, WebKit)
playwright install
```

---

### 5. Upload the Project Files

You’ll need to create and upload the following two scripts:

#### `app.js` (Node.js App on App Server)

[app.js](./app.js)

Start the server:

```bash
node app.js
```

---

#### `worker.py` (Python Worker on Worker Server)
[worker.py](./worker.py)

Run the worker:

```bash
python3 worker.py
```

---

## 6. Configure S3 Bucket for Public Access

Because your bucket uses **Object Ownership: Bucket owner enforced**, ACLs like `'public-read'` will fail.

Instead, apply this **bucket policy** to allow public read access:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowPublicRead",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::screenshot-bucket-indra/*"
    }
  ]
}
```

---

## 7. Test the Service

From Postman or curl:

```bash
curl -X POST http://<App_Instance_Public_IP>:3000/screenshot \
     -H "Content-Type: application/json" \
     -d '{"url": "https://example.com"}'
```

Then check your S3 bucket — the screenshot should be there and viewable publicly.

---

## Optional Improvements

* Add logging and retry logic in the worker
* Use pre-signed URLs instead of public access
* Add a frontend to submit URLs
* Use Elastic Beanstalk for easier deployment
* Auto-start worker as a service on boot

---