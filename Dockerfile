FROM mcr.microsoft.com/windows/servercore:ltsc2022

SHELL ["powershell", "-Command"]

# Install Python (silent install)
RUN Invoke-WebRequest -Uri https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe -OutFile python-installer.exe ; \
    Start-Process -Wait -FilePath .\python-installer.exe -ArgumentList '/quiet InstallAllUsers=1 PrependPath=1' ; \
    Remove-Item python-installer.exe

# Confirm Python and pip installed
RUN python --version ; pip --version

# Set working directory
WORKDIR /app

# Copy all project files into the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run your script (change this if needed)
CMD ["python", "main.py"]
