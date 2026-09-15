# AutoValue Vehicles

A full-stack Django web application for listing, evaluating, and purchasing used vehicles in Ireland, supported by a cloud-based DevSecOps deployment workflow.

## Key Technologies

**Django** • **Python** • **AWS EC2** • **GitHub Actions** • **Nginx** • **Gunicorn** • **Pylint** • **Bandit** • **Linux** • **SSH**

## 1. Project Overview

**AutoValue Vehicles** provides an end-to-end vehicle marketplace workflow for three user roles:

- **Seller** – submits vehicles and supporting information/images.
- **Manager** – reviews submitted vehicles, performs valuation, manages buyer selection, and oversees the deal process.
- **Buyer** – browses available vehicles and expresses interest in vehicles listed on the marketplace.

The project also demonstrates a practical **Cloud DevSecOps architecture**, combining GitHub-based version control, GitHub Actions CI/CD, static code analysis, security analysis, and deployment to an AWS EC2 environment.

### Project Baseline

The project baseline was established as a functional Django vehicle marketplace deployed on AWS EC2. The DevSecOps work then focused on improving automation, code quality, security awareness, and deployment reliability.

---

## 2. DevSecOps Architecture

The deployment workflow is implemented using **GitHub Actions** and is divided into Continuous Integration (CI) and Continuous Deployment (CD).

### Continuous Integration (CI)

The CI stage is triggered by pushes to the `main` branch and can also be started manually.

The current workflow performs:

1. Checkout of the source code.
2. Python 3.11 environment setup.
3. Installation of application dependencies.
4. Django system checks using `python manage.py check`.
5. Static code analysis using **Pylint**.
6. Security analysis using **Bandit**.

> **Note:** Flake8 is currently installed by the workflow but is not executed as a separate analysis step. It is therefore not described as an active CI check in this README.

### Continuous Deployment (CD)

After the CI job completes, the deployment job:

1. Establishes an SSH connection from GitHub Actions to the AWS EC2 instance using the `EC2_SSH_KEY` GitHub Secret.
2. Connects to the application directory on EC2.
3. Fetches the latest `main` branch.
4. Synchronises the working tree using:
   ```bash
   git fetch origin main
   git reset --hard origin/main
   ```
5. Activates the Python virtual environment.
6. Installs the latest application dependencies.
7. Applies Django database migrations.
8. Collects static files.
9. Restarts the Gunicorn service.

This approach keeps deployment automated and avoids manual code copying to the server.

### SSH Deployment Model

The deployment uses two separate SSH trust relationships:

- **GitHub Actions → EC2:** GitHub Actions uses the `EC2_SSH_KEY` repository secret to access the EC2 server.
- **EC2 → GitHub:** The EC2 server uses its configured Git credentials/deploy key to retrieve the repository.

No private SSH key should be committed to this repository.

---

## 3. AWS Deployment Architecture

The application is hosted on an **AWS EC2** Linux instance.

### Nginx

Nginx acts as the web-facing reverse proxy. It:

- Handles incoming HTTP requests.
- Serves static files.
- Serves uploaded media files.
- Proxies dynamic application requests to Gunicorn.

### Gunicorn

Gunicorn provides the WSGI application server for Django.

It is configured as a Linux `systemd` service so that it can be:

- Started and stopped using `systemctl`.
- Restarted automatically as part of deployment.
- Managed independently from the Nginx web server.

### High-Level Flow

```text
User Browser
     |
     v
   Nginx
     |
     +---- /static/ and /media/ ---> EC2 Storage
     |
     v
  Gunicorn
     |
     v
 Django Application
     |
     v
 SQLite Database
```

---

## 4. Application Features

### 4.1 Role-Based Access Control

The application provides role-specific functionality for:

- Seller
- Manager
- Buyer

Access and workflows are implemented through the Django authentication system and application-level role checks.

### 4.2 Vehicle Submission

Sellers can submit used vehicles with information including:

- Registration number
- Vehicle type
- Make and model
- Colour
- Fuel type
- Kilometres travelled
- Expected selling price
- Address information
- Vehicle images

### 4.3 Vehicle Valuation

Managers review submitted vehicles and provide valuation information.

The valuation logic is implemented in the vehicle service layer through:

```text
vehicles/services/valuation.py
```

The application uses the original purchase date and purchase price as inputs to the residual-value calculation.

### 4.4 Marketplace and Deal Management

The application supports the following workflow:

1. A vehicle is submitted by a seller.
2. A manager reviews and evaluates the vehicle.
3. The vehicle becomes available to buyers.
4. Buyers can express interest.
5. The manager selects a buyer.
6. The deal is locked for the selected buyer.
7. The seller confirms the required banking information.
8. The ownership handover process is tracked by the application.

---

## 5. Project Structure

```text
AutoValueVehicles/
├── .github/
│   └── workflows/
│       └── deploy.yml
├── accounts/
│   ├── migrations/
│   ├── forms.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── autovalue/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── deals/
│   ├── migrations/
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── media/
│   └── vehicles/
├── reports/
├── templates/
├── vehicles/
│   ├── migrations/
│   ├── services/
│   │   └── valuation.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
├── .gitignore
├── .pylintrc
├── manage.py
├── requirements.txt
└── seed_data.py
```

---

## 6. Local Development Setup

### Prerequisites

- Python 3.10 or later
- Git
- pip
- A virtual environment

### Installation

```bash
git clone https://github.com/bijin-babu/AutoValue-Vehicles.git
cd AutoValue-Vehicles

python -m venv venv
```

Activate the virtual environment.

**Windows:**
```powershell
.\venv\Scripts\activate
```

**Linux/macOS:**
```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Set required environment variables:

**Windows (PowerShell):**
```powershell
$env:DJANGO_SECRET_KEY="replace-with-a-development-secret"
$env:DEBUG="True"
$env:ALLOWED_HOSTS="127.0.0.1,localhost"
$env:DEMO_PASSWORD="replace-with-a-demo-password"
```

**Linux/macOS:**
```bash
export DJANGO_SECRET_KEY="replace-with-a-development-secret"
export DEBUG="True"
export ALLOWED_HOSTS="127.0.0.1,localhost"
export DEMO_PASSWORD="replace-with-a-demo-password"
```

Apply migrations:

```bash
python manage.py migrate
```

Create an administrator account:

```bash
python manage.py createsuperuser
```

Run the development server:

```bash
python manage.py runserver
```

The application is then available locally at:

```text
http://127.0.0.1:8000/
```

---

## 7. Test Data

A `seed_data.py` script is provided to create demonstration users and sample vehicle data.

Demo credentials are supplied through the `DEMO_PASSWORD` environment variable and are not stored in the repository.

Example:

```bash
python manage.py shell < seed_data.py
```

---

## 8. Code Quality and Security

### Pylint

Pylint is used to identify code-quality issues such as:

- Unused imports
- Incorrect import ordering
- Unnecessary control-flow structures
- Maintainability and style issues

The project also contains a `.pylintrc` configuration file to customise analysis for the Django project.

### Bandit

Bandit is used for Python security analysis.

The final recorded Bandit scan identified **three low-severity B105 hardcoded-password findings**, all located in test code. No medium- or high-severity findings were reported in that scan. These findings were limited to test data rather than production credentials and were retained as evidence of the security-analysis process documented in the academic report.

---

## 9. CI/CD Workflow

The workflow is defined in:

```text
.github/workflows/deploy.yml
```

### CI

```text
Checkout
   |
   v
Python 3.11
   |
   v
Install Dependencies
   |
   v
Django Checks
   |
   v
Pylint
   |
   v
Bandit
```

### CD

```text
CI completed
   |
   v
SSH to EC2
   |
   v
Fetch latest main
   |
   v
Reset working tree
   |
   v
Install dependencies
   |
   v
Migrate database
   |
   v
Collect static files
   |
   v
Restart Gunicorn
```

The current Pylint and Bandit commands use `|| true`, meaning their findings are reported without failing the CI job. This was useful during iterative remediation, but a future production-oriented improvement would be to introduce explicit quality and security gates.

---

## 10. Security and Repository Hygiene

The repository is intended to contain source code and configuration, **not credentials or private infrastructure keys**.

Do not commit:

- `.pem` private keys
- Git deploy private keys
- AWS credentials
- Django production secret keys
- Real user passwords
- Real IBAN/banking information
- Production database files
- Private server credentials

Sensitive configuration should be supplied through environment variables, GitHub Secrets, or an appropriate server-side secret-management mechanism.

---

## 11. Future Improvements

Potential improvements include:

- Docker and container-based deployment.
- PostgreSQL instead of SQLite for production workloads.
- Automated unit/integration testing as a CI gate.
- Explicit Pylint quality thresholds.
- Bandit severity-based security gates.
- Dynamic Application Security Testing (DAST).
- AWS CloudWatch monitoring and centralised logging.
- Infrastructure as Code using Terraform.
- Deployment rollback/versioning.
- HTTPS/TLS using an appropriate certificate configuration.
- Separate development and production Django settings.

---

## 12. Technologies Used

| Category | Technology |
|---|---|
| Application | Django |
| Language | Python |
| Front End | HTML, Bootstrap 5 / Django Templates |
| Database | SQLite |
| Web Server | Nginx |
| Application Server | Gunicorn |
| Cloud | AWS EC2 |
| CI/CD | GitHub Actions |
| Code Quality | Pylint |
| Security Analysis | Bandit |
| Version Control | Git / GitHub |
| Deployment | SSH + systemd |

---

## 13. Academic Project Context

This project demonstrates the application of Cloud Computing, DevOps and DevSecOps principles to a functional web application. The main focus was not only on implementing application functionality, but also on automating delivery, incorporating security analysis into the development lifecycle, and deploying the application to a cloud-hosted environment.

The project therefore provides a practical example of how software development, cloud infrastructure, continuous integration, continuous deployment, static analysis and security practices can be combined into a single development lifecycle.
