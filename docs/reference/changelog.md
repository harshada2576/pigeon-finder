# Changelog (Release Notes)

This document details all significant changes, features, improvements, and fixes for **[Your Project Name]**.

---

## Version 2.0.0 (October 5, 2025) - Major Release

### ✨ Features
* **Decoupled Data Layer:** Introduced Service Interfaces to fully decouple business logic from the Data Layer.
* **Multi-Tenant Support:** Added official support for running the application in a multi-tenant environment using a new `TenantID` context object.
* **New CLI Command:** Added `your-project-name upgrade` to streamline the update process.

### ⚠️ Breaking Changes
* The `PROJECT_PORT` environment variable is now deprecated. Please use `SERVER_PORT` instead (see **[Configuration Guide](../getting-started/configuration.md)**).
* The `UserService.get_all_users()` method now requires a `limit` parameter.

### 🔨 Bug Fixes
* Fixed an issue where large files would sometimes truncate during processing jobs (Issue #105).

---

## Version 1.1.0 (August 15, 2025) - Minor Update

### ✨ Features
* **S3 Storage Support:** Added a new data connector for Amazon S3 storage backends.
* Improved logging format to include timestamps and log level in all output.

### 🔨 Bug Fixes
* Resolved a race condition in the Dispatcher when handling simultaneous requests.
* Corrected internal links in the **[Contributing Guide](../development/contributing.md)**.