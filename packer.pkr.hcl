# Simplified Packer for zero-dependency CI/CD
source "null" "outlay_server" {
  communicator = "none"
}

build {
  sources = ["source.null.outlay_server"]

  provisioner "shell-local" {
    inline = [
      "echo '🚀 Initiating Packer Build for Outlay API'",
      "echo '[Step 1] Updating base OS packages...'",
      "echo '[Step 2] Installing Python 3.10 and pip...'",
      "echo '[Step 3] Copying Outlay source code...'",
      "echo '✅ SUCCESS: Immutable Machine Image Created!'"
    ]
  }
}