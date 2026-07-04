# Contributing Guidelines

Thank you for your interest in contributing to the Smart Traffic Management System project!

---

## 1. Code Style Guidelines

- **Python**: Follow PEP 8 rules. Add docstrings to all files, classes, and methods. Keep code modular.
- **Node.js**: Use ES Modules (import/export). Maintain clean middleware patterns.
- **React**: Structure components as functional components. Keep component styling modular.

---

## 2. Development Workflow

1. Fork the repository.
2. Create a feature branch: `git checkout -b feature/your-feature-name`.
3. Verify your changes pass all diagnostics tests:
   ```bash
   python run_pipeline.py
   ```
4. Commit your files: `git commit -m "Add descriptive feature message"`.
5. Push to GitHub and submit a Pull Request (PR).

---

## 3. Pull Request Standards

- Explain the feature or bug fix clearly.
- Provide verification screenshots or logs indicating success.
- Ensure the PR builds cleanly without breaking existing test scripts.
