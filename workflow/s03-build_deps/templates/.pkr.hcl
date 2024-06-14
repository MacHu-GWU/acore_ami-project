packer {
  required_plugins {
    amazon = {
      source  = "github.com/hashicorp/amazon"
      version = "~> 1"
    }
  }
}

source "amazon-ebs" "ubuntu" {
  ami_name      = var.output_ami_name
  instance_type = "t3.2xlarge"
  region        = var.aws_region
  ssh_username  = "ubuntu"

  /*----------------------------------------------------------------------------
  You can either explicitly specify the ``source_ami`` field or use the ``source_ami_filter``
  to find the AMI ID automatically. I personal prefer to provide the ``source_ami``
  explicitly for better control.
  https://developer.hashicorp.com/packer/integrations/hashicorp/amazon/latest/components/builder/ebs
  ----------------------------------------------------------------------------*/
  source_ami = var.source_ami_id

  # if none default VPC, you need to explicitly set this to true
  associate_public_ip_address = true

  # make sure you are using a public subnet
  subnet_filter {
    filters = {
      "tag:Name": var.subnet_name,
    }
    most_free = true
    random = false
  }

  # make sure the security group has ssh inbound rule
  security_group_filter {
    filters = {
      "tag:Name": var.security_group_name,
    }
  }
}

build {
  name    = "install build dependencies"
  sources = [
    "source.amazon-ebs.ubuntu"
  ]

  # see more details at https://www.azerothcore.org/wiki/linux-requirements
  provisioner "shell" {
    inline = [
      # wait until the machine fully boots up
      "sleep 10",
      "sudo apt-get update -y",
      # note, we don't install MySQL via apt-get, it is already installed in the previous AMI
      # libboost-all-dev might have some dependencies issue, we can fix the dependencies by using "sudo apt --fix-broken install -y"
      # and then install again, that's why we run this command twice
      "sudo apt-get install git cmake make gcc g++ clang libmysqlclient-dev libssl-dev libbz2-dev libreadline-dev libncurses-dev libboost-all-dev -y || sudo apt --fix-broken install -y",
      "sudo apt-get install git cmake make gcc g++ clang libmysqlclient-dev libssl-dev libbz2-dev libreadline-dev libncurses-dev libboost-all-dev -y || sudo apt --fix-broken install -y",
      # Print the versions of the installed dependencies
      "echo check ubuntu version ...",
      "lsb_release -a",
      "echo check openssl version ...",
      "openssl version",
      "echo check boost version ...",
      "dpkg -s libboost-dev | grep 'Version'",
      "echo check clang version ...",
      "clang --version",
      "echo check cmake version ...",
      "cmake --version",
      "echo check screen version ...",
      "screen --version",
      "echo check mysql version ...",
      "mysql --version",
    ]
  }

  provisioner "file" {
    source = "export_build_deps_versions.py"
    destination = "/tmp/export_build_deps_versions.py"
  }

  provisioner "shell" {
    script = "export_build_deps_versions.sh"
  }
}