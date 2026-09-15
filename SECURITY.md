# Security notes

This repository is a prototype. Please do not upload real customer documents, confidential packaging data, credentials, or API keys to issues or pull requests.

## Before a production deployment

- Keep secrets outside the repository and rotate any accidentally exposed credentials.
- Validate file types using both MIME information and decoded image content.
- Add authentication and authorization around stored scans and reports.
- Add rate limiting and request-size limits.
- Strip EXIF metadata when images are retained.
- Encrypt stored images and reports.
- Define a retention/deletion policy.
- Log security-relevant events without storing unnecessary personal data.
- Review the legal-rule data against the latest applicable official sources.
