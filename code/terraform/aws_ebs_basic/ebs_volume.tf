resource "aws_volume_attachment" "w2v_ebs_att" {
  device_name = "/dev/sdh"
  volume_id   = aws_ebs_volume.w2v_ebs_vol.id
  instance_id = aws_instance.w2v-server.id
}

resource "aws_ebs_volume" "w2v_ebs_vol" {
  availability_zone = var.availabilty_zone
  size              = 1
}