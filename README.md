# DOCX to PDF Converter API

This service provides API to convert DOCX files to PDF format using LibreOffice

## Run Steps

1. Run `docker compose up --build` to start the service using docker
2. Run `fastapi dev` to start without docker

### Dependencies

| Software    | Version |
| ----------- | ------- |
| LibreOffice | latest  |
| Python      | 3.11+   |

### Ports

| Service | Port |
| ------- | ---- |
| API     | 8000 |

### Environment Variables

| Environment Variable | Description                     | Default Value |
| -------------------- | ------------------------------- | ------------- |
| PORT                 | Port on which service runs     | 8000          |
| LOG_LEVEL           | Logging level                   | INFO          |

## Monitoring URLs

| Type        | URL            | Expected Response Code | Sample Response |
| ----------- | -------------- | ---------------------- | --------------- |
| Healthcheck | `/healthcheck` | 200                    | "success"       |
| API Docs    | `/docs`        | 200                    | Swagger UI      |

## Service Dependencies:

### Upstream

1. Client applications sending DOCX files

### Downstream

1. LibreOffice (for PDF conversion)
