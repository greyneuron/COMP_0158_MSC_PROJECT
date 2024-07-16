1. VPC > EC2 (main and securoty group)
    - Run 'terraform apply' on the vpc module
    - Take the outputs, for example
    
    vpc_id = "vpc-01ede11f2f41296af"
        > Use in w2v_ec2/main.tf
        > Use in w2v_ec2/security_group.tf

    w2v_private_subnet_id = "subnet-08b78d61650c716cf"

    w2v_public_subnet_id = "subnet-0858c958d9bbbdae9"
        > Use in w2v_ec2/security_group.tf

    w2v_rds_subnet_1 = "subnet-0fd63075992f3e124"

    w2v_rds_subnet_2 = "subnet-013fb8a61d8259bfd"

2. EBS > EC2
    - Run 'teraform apply' on the ebs module
    - Take the following outputs and paste the id into ec2 aws_volume_attachment

        > id=vol-05f27d34631d31dd8

    - Subnet groups
        > Paste 2 ids into RDS
    
    - Security group
        > paste into RDS (public sec grp)

3. EC2

