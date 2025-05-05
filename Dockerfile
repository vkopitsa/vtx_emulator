FROM python:3.9-slim

WORKDIR /app

# Copy the project files
COPY . .

# Make scripts executable
RUN chmod +x main_port.py run_emulator.py examples/custom_vtx_config.py examples/client_example.py

# Expose the default port
EXPOSE 5762

# Set the entrypoint to the main script
ENTRYPOINT ["python", "main_port.py"]
