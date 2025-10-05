# Frequently Asked Questions (FAQ)

This page provides answers to the most common questions about **[Your Project Name]**.

## Installation and Setup

### Q: Why is the installation command failing with a permissions error?

**A:** This usually means you are trying to install the package globally without the necessary administrative rights.

**Solution:**
1.  Try running the install command with administrative privileges (e.g., `sudo pip install package-name` on Linux/macOS, or running the terminal as Administrator on Windows).
2.  Alternatively, use a virtual environment (`venv`, `conda`, etc.) to install the package in your user space, which is the recommended practice for development.

### Q: I configured the port, but the service still starts on 8080. Why?

**A:** This is likely a precedence issue. Check the following:
1.  Ensure your environment variable (`PROJECT_PORT`) is set **before** you execute the run command.
2.  If you are using a configuration file, check if the value in the file is overriding the environment variable, or vice-versa, depending on how your application loads settings (see the **[Configuration Guide](../getting-started/configuration.md)**).

## Usage and Errors

### Q: How do I access the raw data after a processing job is complete?

**A:** The output files are saved to the directory specified by the `OUTPUT_PATH` setting in your configuration. By default, this is `./output/jobs/`.

The data structure within that folder is: `[OUTPUT_PATH]/<job_id>/data.csv`.

### Q: I received a "401 Unauthorized" error when using the API.

**A:** This indicates an issue with your API credentials.
* Check that you are including a valid **API key or token** in the `Authorization` header of your request.
* Ensure the key has the necessary **scopes or permissions** for the endpoint you are trying to access.

## Contribution

### Q: Can I contribute to the documentation itself?

**A:** Absolutely! We welcome documentation improvements. Please read the **[Contributing Guide](../development/contributing.md)** and the **[Documentation Style Guide](./style-guide.md)**, then open a Pull Request with your suggested changes.