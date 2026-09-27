AWS Systems Manager Agent
=========

[![CI](https://github.com/deekayen/ansible-aws-ssm/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-aws-ssm/actions/workflows/ci.yml) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

Install AWS EC2 Systems Manager (SSM) agent

http://docs.aws.amazon.com/systems-manager/latest/userguide/ssm-agent.html

Requirements
------------

GnuPG is installed at runtime.

Role Variables
--------------

Available variables are listed below, along with default values:

```
# The defaults provided by this role are specific to each distribution.
url: amd64
disable_gpg_check: false
gpg_key_url: ""
gpg_key_fingerprint: 1c5b395cbe5e74e2f1ca21592784dbf388d19d46
```

AWS publishes the SSM Agent signing key only in its
[signature verification docs](https://docs.aws.amazon.com/systems-manager/latest/userguide/verify-agent-signature.html),
not on a keyserver, so the role bundles it in `files/amazon-ssm-agent.gpg`.
The bundled key expires 2027-11-25. The role picks the arm64 package on
aarch64 hosts automatically.

Tested with Molecule on EL 9, Amazon Linux 2023, Ubuntu 22.04/24.04/26.04,
and Debian 12/13. EL 10 is not supported: AWS's current signing key carries
only SHA-1 signatures, which the EL 10 default crypto policy rejects, so
`rpm --import` of the key fails there.

For installation in [Raspbian](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-manual-agent-install.html#agent-install-raspbianjessie), please find the activation code and id before using this role
```
url: arm
aws_ssm_activation_code: ''
aws_ssm_activation_id: ''
aws_ssm_ec2_region: "{{ ec2_region }}"
```


Dependencies
------------

None

Example Playbook
----------------

Amazon only keeps a signing key for a year or two. When this role is outdated and you're waiting for an update, point `gpg_key_url` at a copy of the new key and set its fingerprint at runtime like so:

    - hosts: linuxfarm
      roles:
         - role: deekayen.aws-ssm
           vars:
              gpg_key_url: https://example.com/amazon-ssm-agent.gpg
              gpg_key_fingerprint: <new key fingerprint from the AWS docs>
              aws_ssm_activation_code: activationcode_here
              aws_ssm_activation_id: myactivation_id
              aws_ssm_ec2_region: us-east-1


License
-------

MIT

Author Information
------------------

https://www.github.com/dhoeric
