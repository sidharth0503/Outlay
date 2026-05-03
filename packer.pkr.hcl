# packer.pkr.hcl

packer {
  required_plugins {
    null = {
      version = ">= 1.0.0"
      source  = "github.com/hashicorp/null"
    }
  }
}

# The 'null' source simulates a machine instance without requiring cloud credentials
source "null" "outlay_server" {
  communicator = "none"
}

build {
  name = "outlay-api-build"
  sources = ["source.null.outlay_server"]

  # Here we define the steps Packer WOULD take to configure the server
  provisioner "shell-local" {
    inline = [
      "echo '============================================'",
      "echo '🚀 Initiating Packer Build for Outlay API'",
      "echo '============================================'",
      "echo '[Step 1] Updating base OS packages...'",
      "echo '[Step 2] Installing Python 3.10 and pip...'",
      "echo '[Step 3] Copying Outlay source code to /opt/outlay...'",
      "echo '[Step 4] Installing dependencies from requirements.txt...'",
      "echo '[Step 5] Configuring systemd to run Outlay on 0.0.0.0:5000...'",
      "echo '============================================'",
      "echo '✅ SUCCESS: Immutable Machine Image Created!'",
      "echo '============================================"
    ]
  }
}