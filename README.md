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
gpg_key_url: https://keyserver.ubuntu.com/pks/lookup?op=get&search=0x2bc7c7c267bbd505eaa491e6dd81a61756baa549
gpg_key_fingerprint: 2bc7 c7c2 67bb d505 eaa4  91e6 dd81 a617 56ba a549
aws_ssm_agent_version: latest
```

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

Amazon only keeps a signing key for a year or two. When this role is outdated and you're waiting for an update, you can override the signing key URL at runtime like so:

    - hosts: linuxfarm
      roles:
         - role: deekayen.aws-ssm
           vars:
              gpg_key_url: https://keys.openpgp.org/vks/v1/by-fingerprint/2BC7C7C267BBD505EAA491E6DD81A61756BAA549
              aws_ssm_agent_version: 3.0.1390.0
              aws_ssm_activation_code: activationcode_here
              aws_ssm_activation_id: myactivation_id
              aws_ssm_ec2_region: us-east-1


License
-------

MIT

Author Information
------------------

https://www.github.com/dhoeric
