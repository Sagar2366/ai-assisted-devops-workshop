# Intentionally insecure Terraform configuration for security scanning demos
# DO NOT apply this to any real AWS account

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      # No version constraint - uses whatever is installed
    }
  }
}

provider "aws" {
  region     = "us-east-1"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

# Public S3 bucket with no encryption
resource "aws_s3_bucket" "data" {
  bucket = "my-company-sensitive-data"
  tags = {
    Name = "Sensitive Data Bucket"
  }
}

resource "aws_s3_bucket_acl" "data" {
  bucket = aws_s3_bucket.data.id
  acl    = "public-read-write"
}

# No versioning enabled
# No server-side encryption
# No access logging
# No lifecycle rules
# No public access block

# Wide-open security group
resource "aws_security_group" "allow_all" {
  name        = "allow-all-traffic"
  description = "Allow all inbound and outbound traffic"
  vpc_id      = "vpc-12345678"

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all TCP from anywhere"
  }

  ingress {
    from_port   = 0
    to_port     = 65535
    protocol    = "udp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all UDP from anywhere"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# RDS instance with public access and no encryption
resource "aws_db_instance" "main" {
  identifier     = "production-database"
  engine         = "mysql"
  engine_version = "8.0"
  instance_class = "db.t3.medium"

  db_name  = "appdb"
  username = "admin"
  password = "Password123!"  # Hardcoded password

  publicly_accessible    = true
  skip_final_snapshot    = true
  deletion_protection    = false
  storage_encrypted      = false
  multi_az               = false
  backup_retention_period = 0

  vpc_security_group_ids = [aws_security_group.allow_all.id]

  # No performance insights
  # No enhanced monitoring
  # No auto minor version upgrade
}

# Overly permissive IAM policy
resource "aws_iam_policy" "admin_policy" {
  name        = "full-admin-access"
  description = "Full administrative access"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_user" "deploy_user" {
  name = "deploy-user"
}

resource "aws_iam_user_policy_attachment" "deploy_admin" {
  user       = aws_iam_user.deploy_user.name
  policy_arn = aws_iam_policy.admin_policy.arn
}

# EC2 instance with public IP and no IMDSv2
resource "aws_instance" "web" {
  ami           = "ami-12345678"
  instance_type = "t3.xlarge"  # Potentially over-provisioned

  associate_public_ip_address = true
  vpc_security_group_ids      = [aws_security_group.allow_all.id]

  # No IMDSv2 enforcement (SSRF vulnerability)
  # metadata_options not configured

  # No encryption for root volume
  root_block_device {
    volume_size = 100
    encrypted   = false
  }

  # User data with secrets
  user_data = <<-EOF
    #!/bin/bash
    echo "DB_PASSWORD=Password123!" >> /etc/environment
    curl -H "X-Api-Key: sk-prod-12345abcdef" https://api.example.com/setup
  EOF

  tags = {
    Name = "web-server"
  }
}
