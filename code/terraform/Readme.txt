1. VPC > EC2 (main and securoty group)
    - Run 'terraform apply' on the vpc module
    - Take the outputs, for example
    
    vpc_id = "vpc-01ede11f2f41296af"
        > Use in w2v_ec2/security_group.tf
    
    w2v_public_subnet_id = "subnet-0858c958d9bbbdae9"
        > Use in w2v_ec2/main.tf



2. EBS > EC2
    - Run 'teraform apply' on the ebs module
    - Take the following outputs and paste the id into ec2 aws_volume_attachment

        > id=vol-05f27d34631d31dd8

    - Subnet groups
        > Paste 2 ids into RDS
    
    - Security group
        > paste into RDS (public sec grp)

3. EC2


4. RDS


SSH to EC@ instance
    % ssh -i "w2v_rsa" ec2-user@<take from ouput of starting ec2>


Now execute the following:
sudo dnf update -y
sudo dnf install mariadb105

Get the RDS endpoint. For example: w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com

NOTE: I HASD TO MAKE THE CONNECTION MYSELF

mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u admin -p

mysql -h w2v-dev-db.cligs4ak0dtg.eu-west-1.rds.amazonaws.com -P 3306 -u w2v -p

S3 Lambda
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html