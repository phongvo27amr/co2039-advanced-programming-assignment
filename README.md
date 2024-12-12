# Install Docker and Docker Compose

- Verify Docker is installed:

```
docker --version
docker-compose --version
```

# Run the app

- Clone or download the repository:

```
git clone https://github.com/phongvo27amr/co2039-advanced-programming-assignment.git
cd co2039-advanced-programming-assignment
```

- Build and run the app:

  - This builds the Docker image and starts the container
  - The app will be accessible at http://localhost:5000

```
docker-compose up --build
```

# Stop the app

- Press Ctrl+C in the terminal or use:

```
docker-compose down
```
