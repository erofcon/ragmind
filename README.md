## 💡 What is RAGMind?

RAGMind is an open-source Retrieval-Augmented Generation (RAG) engine designed for in-depth document comprehension. It
provides an optimized RAG workflow suitable for businesses of any size, leveraging Large Language Models (LLMs) to
deliver accurate question-answering capabilities, supported by reliable citations from complexly formatted data sources.

## 🚧 Project in Development 🚧

> **⚠️ Warning:** This project is currently under active development and may be unstable.
> It is not recommended for production use at this stage, as features and functionality
> are still evolving and subject to significant changes. Please use it for testing and development purposes only.

## 🌟 Key Features

### 🍭 **"Quality in, quality out"**

- Extracts knowledge from unstructured data with complex formats through deep document understanding.
- Locates the "needle in a data haystack," handling virtually limitless tokens.

### 🌱 **Reliable citations with minimized hallucinations**

- Visual text chunking enables human oversight.
- Quick access to key references and traceable citations, supporting accurate answers.

### 🛀 **Effortless and Automated RAG Workflow**

- Simplified RAG orchestration tailored for individuals and enterprises alike.
- Customizable LLMs and embedding models.
- Multi-step retrieval with enhanced re-ranking fusion.
- User-friendly APIs for smooth business integration.

### 📝 Prerequisites

- CPU >= 4 cores
- RAM >= 16 GB
- Disk >= 50 GB
- Docker >= 24.0.0 & Docker Compose >= v2.26.1
  > If you have not installed Docker on your local machine (Windows, Mac, or Linux),
  see [Install Docker Engine](https://docs.docker.com/engine/install/).

### ⚙️ CUDA Recommendation

> **Recommendation:** For optimal performance, it is recommended to install **NVIDIA CUDA version 12.1 or higher**.
> You can find installation instructions and further details in
> the [official NVIDIA CUDA documentation](https://developer.nvidia.com/cuda-toolkit).

### 🚀 Start up the server

1. Clone the repo:

   ```bash
   git clone https://github.com/erofcon/ragmind.git

2. Go to project:
    ```bash
   cd ragmind
   ```

3. Build the pre-built Docker images and start up the server:
    ```bash
   cd docker
   docker compose -f docker-compose.yml up -d
   ```

4. Install requirements:
    ```bash
   pip install -r requirements.txt
   ```

## ⚠️ Important

> **⚠️ Please ensure** you are installing the correct version of PyTorch with CUDA support compatible with your system.
> Using an incorrect version may lead to errors or reduced performance.
>
> To install PyTorch with CUDA, use the following command, replacing `cu121` with the appropriate CUDA version:
> ```bash
> pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
> ```
> For the latest installation commands, visit the [official PyTorch page](https://pytorch.org/get-started/locally/).

## Database Migrations

If you need to set up database migrations from scratch, use the following commands. However, **the first two steps are
optional** if the migration setup already exists.

1. Initialize Alembic with async support (optional if already set up):
    ```bash
    alembic init -t async migrations
    ```
2. Generate an initial migration script (optional if migrations already exist):
    ```bash
    alembic revision --autogenerate -m "init"
    ```
3. Apply the migrations to the database:
    ```bash
    alembic upgrade head
    ```

## 🌐 Web Interface Setup

> **Note:** If you'd like to launch the web interface for this project, please follow the setup instructions in
> the [dedicated repository here](https://github.com/erofcon/ragmind_web).

## 📄 License

> This project is open-source and distributed under the **MIT License**, which permits free use, modification, and distribution. For more details, please see the [MIT License documentation](https://opensource.org/licenses/MIT).
