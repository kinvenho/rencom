# Rencom - Plug-and-Play E-commerce Reviews API

A modern, scalable API platform for collecting and displaying product reviews for any e-commerce store. No frontend, no platform lock-in—just robust, efficient APIs.

## 🚀 Features

- **API Token Authentication**: Secure, token-based access for all endpoints
- **Product Reviews**: Collect, store, and retrieve reviews for any product
- **Pagination & Performance**: Designed for scale (1k+ users, 15k+ reviews)
- **Supabase Backend**: Real-time, scalable PostgreSQL database
- **FastAPI**: High-performance Python backend
- **Docker-Ready**: Easy local development and deployment
- **CLI Onboarding**: Get started instantly with `rencom setup`

## 🛠️ Installation

### From PyPI (recommended for most users)
```bash
pip install rencom-cli
```

### From Source (for contributors/advanced users)
```bash
git clone <repository-url>
cd rencom
pip install .
```

## ⚡ Quick Start (API Users)

1. **Onboard Instantly**
   ```bash
   rencom setup
   ```
   - This will guide you through API onboarding and create your API token.

2. **Try the API**
   - Use your token to make requests:
   ```bash
   curl -X POST https://rencom-backend.fly.dev/api/v1/reviews \
     -H 'Authorization: Bearer <your-token>' \
     -H 'Content-Type: application/json' \
     -d '{"product_id": "prod-123", "user_id": "user-abc-123", "rating": 5, "comment": "Great!"}'
   ```
   - Or explore the full API in [Postman](https://documenter.getpostman.com/view/your-doc-id)

3. **Shell Completion (Optional)**
   - Enable tab completion for bash, zsh, fish, or PowerShell:
   ```bash
   rencom completion install bash --install
   # See COMPLETION.md for details
   ```

## 👩‍💻 Advanced: Local Development & Forking

If you want to run the API locally, contribute, or self-host:

1. **Fork and Setup Locally**
   ```bash
   rencom fork
   ```
   - This will walk you through forking, configuring, and running the codebase locally.

2. **Manual Setup (for reference)**
   - See the `fork` command or the `api/`, `config/`, and `services/` folders for advanced configuration.

## 📚 API Documentation
- See [PUBLIC_API_DOCS.md](PUBLIC_API_DOCS.md) for full endpoint details.
- Or use the CLI: `rencom help`

## 🤝 Contributing
- Use `rencom fork` to get started as a contributor.
- Standard PR workflow applies.

## 📄 License
MIT License

## 🆘 Support
- Create an issue in the GitHub repository
- Check the API documentation at `/docs` 