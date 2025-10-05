# Documentation Style Guide

This guide outlines the conventions and style rules for writing and maintaining documentation for **[Your Project Name]**. Consistency is key to a great user experience!

## A. Voice and Tone

1.  **Be Direct and Clear:** Use a friendly, professional, and confident tone. Avoid overly technical jargon where a simpler term will suffice.
2.  **Use the Active Voice:** Write sentences in the active voice (e.g., "You must configure the service" instead of "The service must be configured").
3.  **Address the Reader as "You":** Speak directly to the user/developer ("You can find the documentation here.").
4.  **Use Consistent Terminology:** Always refer to project components by their established names (e.g., always "The Dispatcher," never "the router").

## B. Formatting and Markdown

1.  **Headings:** Use `#` for the page title (H1) and `##` for main sections. **Never** use more than one H1 tag per page.
2.  **Code Blocks:**
    * Use triple backticks (```` ``` ````) for all code samples.
    * **Always** specify the language for syntax highlighting (e.g., `` ```python ````, `` ```bash ````).
3.  **Inline Code:** Use single backticks (`` `code` ``) for filenames, commands, function names, and file paths.
4.  **Key Terms:** Use **bold** formatting for new or important terms on their first mention.
5.  **Notes and Warnings:** Use blockquotes or dedicated admonition syntax (if your documentation generator supports it) for special callouts:

    > **Note:** Always run `npm install` before starting the service.
    >
    > **⚠️ Warning:** Do not commit production secrets to Git.

## C. Structure and Organization

1.  **File Naming:** Use **kebab-case** for all file names (e.g., `getting-started/api-keys.md`).
2.  **Internal Links:** Use **relative links** to connect documentation pages (e.g., `[Configuration Guide](../getting-started/configuration.md)`).
3.  **Prerequisites:** Every tutorial and guide should have a clear **Prerequisites** section at the beginning.
4.  **Break Down Steps:** Use numbered lists for sequential steps in tutorials (`1.`, `2.`, `3.`). Use bullet points for non-sequential lists.

## D. Review Checklist

Before submitting a documentation change, please ensure:

* [ ] The change adheres to this Style Guide.
* [ ] All code blocks are correctly highlighted.
* [ ] Relative links point to the correct file path.
* [ ] The language is clear, concise, and in active voice.
* [ ] The document is linked from the `_sidebar.md` (if it's a new page).