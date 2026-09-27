"""Testinfra checks for the AWS SSM agent role."""

KEY_ID = "88d19d46"


def test_agent_package_installed(host):
    assert host.package("amazon-ssm-agent").is_installed


def test_agent_files(host):
    assert host.file("/etc/amazon/ssm").is_directory
    agent = host.file("/usr/bin/amazon-ssm-agent")
    assert agent.is_file
    assert agent.mode == 0o755


def test_signing_key_trusted(host):
    if host.exists("apt-get"):
        key = host.file("/etc/apt/trusted.gpg.d/amazon-ssm-agent.asc")
        assert key.is_file
        assert key.mode == 0o644
        assert key.contains("BEGIN PGP PUBLIC KEY BLOCK")
    else:
        keys = host.check_output("rpm -q gpg-pubkey --qf '%{VERSION}\\n'")
        assert KEY_ID in keys.lower().split()


def test_agent_service_enabled(host):
    assert host.service("amazon-ssm-agent").is_enabled
