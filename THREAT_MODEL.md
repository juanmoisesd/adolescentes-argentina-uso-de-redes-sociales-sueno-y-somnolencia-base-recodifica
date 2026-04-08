# Threat Model

## Assets
1. **Dataset Integrity**: Ensuring data is not tampered with.
2. **Author Identity**: Preventing impersonation.

## Threats
- **Data Tampering**: Malicious actors modifying CSV values.
- **Credential Theft**: Gaining access to the GitHub repository.

## Mitigations
- **Checksums**: SHA256/512 hashes for all files.
- **MFA**: Enabled for repository maintainers.
- **Signed Commits**: All changes must be GPG signed.
