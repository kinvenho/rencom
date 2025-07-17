# Rencom - Plug-and-Play E-commerce Reviews API

A modern, scalable API platform for collecting and displaying product reviews for any e-commerce store. No frontend, no platform lock-in—just robust, efficient APIs.

## 🚀 Features

- **API Token Authentication**: Secure, token-based access for all endpoints
- **Product Reviews**: Collect, store, and retrieve reviews for any product
- **Pagination & Performance**: Designed for scale (1k+ users, 15k+ reviews)
- **Supabase Backend**: Real-time, scalable PostgreSQL database
- **FastAPI**: High-performance Python backend
- **Docker-Ready**: Easy local development and deployment

## 🏗️ Architecture

```
rencom/
├── api/               # FastAPI route handlers
├── config/            # Configuration and settings
├── models/            # Pydantic data models
├── services/          # Business logic (Supabase)
├── utils/             # Helper utilities
├── main.py            # FastAPI application entry point
├── requirements.txt   # Python dependencies
├── Dockerfile         # Containerization
├── docker-compose.yml # Development environment
└── setup.sh           # Setup script
```

## 📋 Prerequisites

- Python 3.8+
- Docker (optional)
- Supabase account

## 🚀 Quick Start

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd rencom
   chmod +x setup.sh
   ./setup.sh
   ```
2. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your Supabase and secret keys
   ```
3. **Set Up Supabase Database**
   ```sql
   -- Reviews table
   CREATE TABLE reviews (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       product_id VARCHAR(255) NOT NULL,
       user_id VARCHAR(255),
       rating INTEGER NOT NULL,
       comment TEXT,
       status VARCHAR(32) DEFAULT 'approved',
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- API Tokens table
   CREATE TABLE api_tokens (
       id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
       token VARCHAR(255) UNIQUE NOT NULL,
       name VARCHAR(255),
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Products table
   CREATE TABLE products (
       id SERIAL PRIMARY KEY,
       product_id VARCHAR(255) UNIQUE NOT NULL,
       name VARCHAR(255),
       created_at TIMESTAMP DEFAULT NOW()
   );

   -- Users table
   CREATE TABLE users (
       id VARCHAR(255) PRIMARY KEY,
       api_token_id UUID REFERENCES api_tokens(id)
   );
   ```
4. **Run the Application**
   ```bash
   python main.py
   # or with Docker
   docker-compose up
   ```
5. **Access the API Docs**
   - http://localhost:8000/docs

## 📚 API Documentation

### Authentication
All API requests require an API token. Include the following header:
```
Authorization: Bearer <your-api-token>
```

### Review Endpoints
- `POST /api/v1/reviews` — Submit a new review (product_id, user_id, rating, comment)
- `GET /api/v1/products/{product_id}/reviews` — Get product reviews (paginated)

## 🗄️ Database Schema
See the Quick Start section for SQL table definitions.

## 🔧 Development
- **api/**: FastAPI route handlers
- **config/**: App configuration
- **models/**: Pydantic models
- **services/**: Supabase integration
- **utils/**: Helper functions

### Development Commands
```bash
python main.py        # Run development server
pytest               # Run tests (when implemented)
```

## 🤝 Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License
MIT License

## 🆘 Support
- Create an issue in the GitHub repository
- Check the API documentation at `/docs`

## 🔮 Roadmap
- ✅ API token authentication
- ✅ Product review endpoints
- ✅ Pagination and performance
- 📅 Admin endpoints for token management
- 📅 Analytics and reporting
- 📅 Advanced filtering and search
- 📅 Multi-language support 
- 📅 Multi-language support 