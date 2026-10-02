# deekayen.aws_ssm

[![CI](https://github.com/deekayen/ansible-aws-ssm/actions/workflows/ci.yml/badge.svg)](https://github.com/deekayen/ansible-aws-ssm/actions/workflows/ci.yml) [![Ansible Galaxy](https://img.shields.io/badge/galaxy-deekayen.aws__ssm-blue.svg)](https://galaxy.ansible.com/ui/standalone/roles/deekayen/aws_ssm/) [![Project Status: Inactive – The project has reached a stable, usable state but is no longer being actively developed; support/maintenance will be provided as time allows.](https://www.repostatus.org/badges/latest/inactive.svg)](https://www.repostatus.org/#inactive)

An Ansible role that installs the AWS Systems Manager agent (`amazon-ssm-agent`) on Linux and, when given a hybrid activation, registers the host as a managed instance.

The role trusts Amazon's package signing key, then installs the `latest` agent package from `s3.amazonaws.com/ec2-downloads-windows/SSMAgent/latest/`: `linux_<arch>/amazon-ssm-agent.rpm` on the RedHat family and `debian_<arch>/amazon-ssm-agent.deb` on Debian and Ubuntu. AWS publishes the signing key only in its [signature verification documentation](https://docs.aws.amazon.com/systems-manager/latest/userguide/verify-agent-signature.html), so the role bundles a copy in `files/amazon-ssm-agent.gpg`.

The Galaxy name is `deekayen.aws_ssm`, with an underscore.

## Requirements

- ansible-core 2.15 or newer on the controller.
- Outbound HTTPS from the target to `s3.amazonaws.com`, plus the URL in `gpg_key_url` if you set one.
- Privilege escalation on the target. Run the play with `become: true`; the role installs packages and writes under `/etc`.
- Fact gathering left on. The role branches on `ansible_facts.os_family`, `ansible_facts.architecture`, and `ansible_facts.userspace_bits`.
- For hybrid registration, an activation code and ID from Systems Manager.

## Supported platforms

From `meta/main.yml`, and each one runs through Molecule in CI:

| Platform | Versions |
| --- | --- |
| EL (Rocky Linux in CI) | 9 |
| Amazon Linux | 2023 |
| Debian | 12 (bookworm), 13 (trixie) |
| Ubuntu | 22.04 (jammy), 24.04 (noble), 26.04 (resolute) |

EL 10 is left out. Per the commit that bundled the key, AWS's signing key carries only SHA-1 signatures, which the EL 10 default crypto policy rejects.

## Installation

From Ansible Galaxy:

```bash
ansible-galaxy role install deekayen.aws_ssm
```

Or pin it in `requirements.yml`:

```yaml
---
roles:
  - name: deekayen.aws_ssm
    src: https://github.com/deekayen/ansible-aws-ssm.git
    scm: git
    version: main
```

```bash
ansible-galaxy role install -r requirements.yml
```

## Role variables

| Variable | Default | Description |
| --- | --- | --- |
| `url` | `amd64` | Architecture segment of the download URL. Must be `amd64`, `386`, `arm`, or `arm64`; the role asserts this. The role replaces it with `386` on any host with a 32-bit userspace, and with `arm64` on `aarch64` hosts when it is still `amd64`. |
| `disable_gpg_check` | `false` | Passed to `dnf` as `disable_gpg_check` when installing the RPM on RedHat-family hosts. |
| `gpg_key_url` | `""` | Empty trusts the bundled key in `files/amazon-ssm-agent.gpg`, which expires 2027-11-25. Set an `http://` or `https://` URL, which the role asserts, to fetch a replacement key after AWS rotates it. |
| `gpg_key_fingerprint` | `1c5b395cbe5e74e2f1ca21592784dbf388d19d46` | Full 40-hex-digit fingerprint, asserted by the role. `rpm_key` checks the imported key against it on the RedHat family. Change it together with `gpg_key_url`. |

### Hybrid activation variables

These have no default. The role registers the host only when both `aws_ssm_activation_code` and `aws_ssm_activation_id` are set and non-empty.

| Variable | Description |
| --- | --- |
| `aws_ssm_activation_code` | Systems Manager hybrid activation code. Keep it in Ansible Vault or a secrets lookup; the register task does not set `no_log`, so the code appears in verbose output. |
| `aws_ssm_activation_id` | Systems Manager hybrid activation ID. |
| `aws_ssm_ec2_region` | Region passed to `amazon-ssm-agent -register`. `tasks/assert.yml` fails the play if it is missing or empty while the code and ID are set. |

## Behavior

- The role installs `gnupg` on every host.
- On the RedHat family, the bundled key is copied to `/etc/pki/rpm-gpg/RPM-GPG-KEY-amazon-ssm-agent` and imported with `rpm_key`. On Debian and Ubuntu, the key goes to `/etc/apt/trusted.gpg.d/amazon-ssm-agent.asc`, from the bundle or from `gpg_key_url`.
- On Debian and Ubuntu, the role enables the `amazon-ssm-agent` service and restarts it after a package install. On the RedHat family, only the registration step restarts the service; no task enables or starts it.
- Registration runs `amazon-ssm-agent -register -clear` only when `/var/lib/amazon/ssm/registration` is absent, then restarts the agent. A host that is already registered is not re-registered with new activation values.

## Dependencies

None.

## Example playbook

Register on-premises hosts with a hybrid activation, using a key fetched from an internal mirror after AWS rotates it:

```yaml
---
- name: Install and register the SSM agent.
  hosts: onprem_managed_nodes
  become: true

  vars:
    gpg_key_url: https://mirror.example.internal/keys/amazon-ssm-agent.gpg
    gpg_key_fingerprint: "{{ ssm_agent_key_fingerprint }}"
    aws_ssm_activation_code: "{{ vault_aws_ssm_activation_code }}"
    aws_ssm_activation_id: "{{ vault_aws_ssm_activation_id }}"
    aws_ssm_ec2_region: us-west-2

  roles:
    - deekayen.aws_ssm
```

`mirror.example.internal`, `ssm_agent_key_fingerprint`, and the `vault_` variables are placeholders. Take the new fingerprint from the AWS signature verification documentation.

## Tags

| Tag | Tasks |
| --- | --- |
| `always` | Input validation. |
| `install_gnupg` | The `gnupg` package install. |
| `import_rpm_key`, `import_apt_key` | Signing key copy and import. |
| `install_ssm_agent` | The agent package install. |
| `register_ssm_agent` | Hybrid activation registration. |
| `enable_ssm_service` | Enabling the service on Debian and Ubuntu. |

## Known issues

- `files/policy.xml` is an ImageMagick `policymap` that no task deploys.
- `tasks/main.yml:7-10` sets `url` to `386` whenever `ansible_facts.userspace_bits` is `32`, which overrides `url: arm` on a 32-bit ARM host such as 32-bit Raspberry Pi OS. Pass `url` as an extra var (`-e url=arm`) to keep it.
- On Debian and Ubuntu, `tasks/main.yml:75-86` downloads the key from `gpg_key_url` into `/etc/apt/trusted.gpg.d/` without checking `gpg_key_fingerprint`, although `meta/argument_specs.yml` says the fingerprint verifies the imported key. Only `rpm_key` on the RedHat family checks it.
- `url: arm` on a RedHat-family host builds `linux_arm/amazon-ssm-agent.rpm`, which returned HTTP 403 when checked on 2026-10-02. The `debian_arm` package returned 200.

## Development

CI runs on every push to `main` and every pull request (see `.github/workflows/ci.yml`):

1. Lint: `ansible-lint --profile production` and `flake8 molecule/`.
2. Molecule: converge, idempotence, and testinfra verification in Docker against each distribution in the table above. The converge playbook sets no activation variables, so CI does not exercise registration.

To run the same checks locally with Docker available:

```bash
pip3 install ansible-core ansible-lint flake8 molecule "molecule-plugins[docker]" docker pytest-testinfra
ansible-lint --profile production
flake8 molecule/
MOLECULE_DISTRO=rockylinux9 molecule test
```

`MOLECULE_DISTRO` selects a `geerlingguy/docker-<distro>-ansible` image. The values CI uses are `rockylinux9`, `amazonlinux2023`, `ubuntu2204`, `ubuntu2404`, `ubuntu2604`, `debian12`, and `debian13`. The testinfra checks in `molecule/default/tests/test_default.py` confirm that the `amazon-ssm-agent` package is installed, `/etc/amazon/ssm` exists, `/usr/bin/amazon-ssm-agent` has mode `0755`, the signing key is trusted (the apt keyring file, or key ID `88d19d46` in the RPM database), and the service is enabled.

### Repository layout

| Path | Purpose |
| --- | --- |
| `tasks/main.yml` | Architecture selection, key import, package install, and service enable. |
| `tasks/assert.yml` | Input validation, tagged `always`. |
| `tasks/register.yml` | Hybrid activation registration. |
| `handlers/main.yml` | Restarts `amazon-ssm-agent`. |
| `files/amazon-ssm-agent.gpg` | Bundled AWS signing key. |
| `defaults/main.yml` | Every user-facing variable with a default. |
| `meta/argument_specs.yml` | Argument spec, including the activation variables. |
| `molecule/default/` | Molecule scenario: `prepare.yml`, `converge.yml`, and testinfra tests. |
| `.github/workflows/` | `ci.yml` for lint and Molecule, `release.yml` for Galaxy import. |

## Releases

Pushing a git tag runs `.github/workflows/release.yml`, which imports the tagged commit into Ansible Galaxy as `deekayen.aws_ssm`. The import needs a `GALAXY_API_KEY` repository or organization secret.

## License

`meta/main.yml` declares MIT, but the repository has no LICENSE file, and the upstream project it was forked from never published a license.

## Authors

[Eric Ho](https://github.com/dhoeric) wrote the original role at [dhoeric/ansible-aws-ssm](https://github.com/dhoeric/ansible-aws-ssm). This repository is forked from [TrentPetersen04/ansible-aws-ssm](https://github.com/TrentPetersen04/ansible-aws-ssm), a fork of that project, and maintained by [David Norman](https://github.com/deekayen). Sponsorship links are in [.github/FUNDING.yml](.github/FUNDING.yml).
