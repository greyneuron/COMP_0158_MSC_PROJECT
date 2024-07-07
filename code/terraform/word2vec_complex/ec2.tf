resource "aws_instance" "web" {
  ami           = var.ami
  instance_type = var.instance_type
  subnet_id     = aws_subnet.main.id

  tags = {
    Name = "web_instance"
  }

  ebs_block_device {
    device_name = "/dev/sdh"
    volume_size = var.ebs_volume_size
  }
}

resource "aws_volume_attachment" "web_attach" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.web_volume.id
  instance_id = aws_instance.web.id
}

resource "aws_ebs_volume" "web_volume" {
  availability_zone = var.availability_zone
  size              = var.ebs_volume_size

  tags = {
    Name = "web_volume"
  }
}
