# Glossary

This glossary defines key terms used across the **[Your Project Name]** documentation and codebase.

| Term | Definition | Context/Related Term |
| :--- | :--- | :--- |
| **Dispatcher** | The central component responsible for mapping incoming requests (from the API or CLI) to the correct service handler. | See **Architecture** |
| **Service Interface** | An abstract class or protocol that defines a contract for a specific set of business operations, decoupling the logic from the data layer. | **Decoupling** |
| **Data Layer** | The part of the application responsible for persistence, including database connections, ORM models, and file storage. | **Persistence** |
| **Job ID (JID)** | A unique identifier (UUID) assigned to every asynchronous task or data processing operation submitted to the system. | **DataProcessorService** |
| **Tenant** | A logical group of users or projects that share access to the same resources, typically used in multi-tenant application deployments. | **Multi-Tenancy** |
| **Kebab-Case** | A naming convention where words are separated by hyphens (e.g., `file-name.md`). This is the preferred style for documentation file names. | **Style Guide** |
| **API Token** | A secure, time-limited string used to authenticate a user or service when making requests to the public interface. | **401 Unauthorized** |

---

## Technical Terms

* **Idempotency:** The property of an operation such that executing it multiple times has the same effect as executing it once. Our `POST /api/v1/jobs` endpoint is designed to be idempotent when using a client-supplied Job ID.
* **Virtual Environment (Venv):** An isolated workspace for your project, allowing you to install dependencies without conflicting with global system packages.

*If you encounter a term that is not defined here but should be, please open a pull request!*