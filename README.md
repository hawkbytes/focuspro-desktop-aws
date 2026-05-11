# DDS Focus Pro v1.7.0 - Time Tracking & Productivity Management System

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/release/python-311/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)](https://flask.palletsprojects.com/)
[![Version](https://img.shields.io/badge/version-1.7.0-blue.svg)](CHANGELOG.md)

## 🚀 Overview

DDS Focus Pro v1.7.0 is a comprehensive time tracking and productivity management system designed to monitor user activities, track program usage, and provide AI-powered insights for better productivity management. The system combines desktop tracking capabilities with a web-based dashboard for real-time monitoring and reporting.

## ✨ New in Version 1.7.0

### ☁️ **Contabo Object Storage Integration**
- **Dual Cloud Storage**: All screenshots and logs now backed up to both AWS S3 and Contabo Object Storage
- **European Data Center**: Using EU2 region for GDPR compliance
- **Enhanced Reliability**: Redundant storage ensures zero data loss
- **Automatic Failover**: Continues operation if either storage provider is unavailable
- **Organized Structure**: Date-based folder hierarchy for easy data management

### 🔧 **Bug Fixes & Improvements**
- Fixed screenshot interval display showing "N/A" in UI
- Updated all UI pages to display v1.7.0
- Improved API endpoint for fetching user-specific screenshot intervals
- Enhanced settings page to dynamically load screenshot interval from backend

## ✨ Features from Version 1.5

### 📸 **Enhanced Screen Capture & Time Tracking**
- **Custom Screenshot Intervals**: Admin-configurable per-user screenshot timing
- **Meeting-Aware Screenshots**: Continue capturing during meetings
- **Total Logged Time**: Comprehensive time tracking from login to logout
- **User Profile Display**: Profile images visible on dashboard

### 🤝 **Advanced Meeting Management**
- **Workflow Integration**: Must stop work before starting meetings
- **Mandatory Project Selection**: Required project/task selection for meetings
- **Meeting Notes**: Capture detailed notes at meeting end
- **Timesheet Integration**: Meeting duration in timesheet reports
- **Smart Idle Handling**: Automatic idle disable during meetings

### 🎨 **Modern User Interface**
- **Dark/Light Mode**: Choose your preferred theme
- **Redesigned Sidebar**: Current project, task, and due date display
- **Expandable Task Details**: Click tasks for comprehensive information
- **Live Screenshot Interval**: Display current capture settings

## ✨ Core Features

### 🖥️ Core Functionality
- **Real-time Activity Tracking**: Monitor active applications and windows
- **Screenshot Capture**: Automated screenshot capture for activity verification
- **Program Usage Analytics**: Detailed analysis of time spent in different applications
- **Idle Time Detection**: Smart detection of user idle periods
- **Database Integration**: Seamless integration with CRM systems

### 🤖 AI-Powered Features
- **Intelligent Project Filtering**: AI-powered project categorization and filtering
- **Smart Summarization**: Automatic generation of activity summaries
- **Natural Language Queries**: SQL generation from natural language prompts
- **Activity Classification**: Automatic categorization of user activities

### 🌐 Web Dashboard
- **Real-time Monitoring**: Live view of user activities
- **Interactive Reports**: Comprehensive reporting with visual analytics
- **User Management**: Multi-user support with email-based authentication
- **Responsive Design**: Modern, mobile-friendly interface

### ☁️ Cloud Integration
- **AWS S3 Storage**: Secure cloud storage for screenshots and logs
- **Email Notifications**: Automated email reports and notifications
- **Data Synchronization**: Real-time data sync across devices

## 🛠️ Technology Stack

- **Backend**: Python 3.11+, Flask
- **Frontend**: HTML5, CSS3, JavaScript
- **Database**: MySQL
- **AI/ML**: OpenAI GPT, scikit-learn, transformers
- **Cloud Services**: AWS S3, Boto3
- **Desktop Integration**: PyAutoGUI, OpenCV, MSS
- **Email**: Flask-Mail
- **Environment Management**: python-dotenv

## 📋 Prerequisites

- Python 3.11 or higher
- MySQL Database
- AWS Account (for S3 storage)
- OpenAI API Key

## 🔧 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/dxdglobal/Client-Side-DDS-Focus.git
cd Client-Side-DDS-Focus
```
### Python 3.11+ required
### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory using the template:
```bash
cp .env.template .env
```

Fill in your configuration values:
```env
# Database Configuration
DB_HOST=your_database_host
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_NAME=your_database_name
DB_PORT=3306

# AWS Configuration
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your_s3_bucket_name

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key

# Email Configuration
MAIL_SERVER=your_mail_server
MAIL_PORT=465
MAIL_USERNAME=your_email_username
MAIL_PASSWORD=your_email_password
MAIL_USE_TLS=False
MAIL_USE_SSL=True
```

### 5. Database Setup
Ensure your MySQL database is running and accessible with the provided credentials.

## 🚀 Usage

### Starting the Application

#### Web Dashboard
```bash
python app.py
```
The web dashboard will be available at `http://localhost:5000`

#### Desktop Tracking
```bash
python desktop.py
```

#### Main Application
```bash
python main.py
```

### 🖱️ Desktop Application Features

1. **Start Tracking**: Begin monitoring user activities
2. **Screenshot Capture**: Automated screenshot functionality
3. **Activity Logging**: Real-time activity logging to database
4. **Idle Detection**: Automatic pause during idle periods

### 🌐 Web Dashboard Features

1. **Login**: Access the dashboard with email authentication
2. **Real-time Monitoring**: View live activity data
3. **Reports**: Generate and view detailed reports
4. **Project Management**: AI-powered project filtering and management
5. **Settings**: Configure tracking preferences

## 📁 Project Structure

```
Client-Side-DDS-Focus/
├── app.py                 # Main Flask web application
├── desktop.py            # Desktop tracking application
├── main.py               # Core application entry point
├── requirements.txt      # Python dependencies
├── .env.template         # Environment variables template
├── .gitignore           # Git ignore rules
├── README.md            # This file
├── moduller/            # Core modules
│   ├── tracker.py       # Activity tracking logic
│   ├── ai_*.py         # AI-powered features
│   ├── veritabani_yoneticisi.py  # Database management
│   └── ...             # Other utility modules
├── templates/           # HTML templates
│   ├── login.html      # Login page
│   ├── client.html     # Main dashboard
│   └── ...             # Other templates
├── static/             # Static assets
│   ├── css/           # Stylesheets
│   ├── js/            # JavaScript files
│   └── images/        # Image assets
└── rules/             # Business rules and configurations
```

## 🔒 Security Features

- **Environment Variables**: All sensitive data stored in environment variables
- **Secure Authentication**: Email-based user authentication
- **Data Encryption**: Secure data transmission and storage
- **Access Control**: User-based access restrictions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

For support and questions:
- Create an issue on GitHub
- Contact: [dxdglobal](https://github.com/dxdglobal)

## 🔄 Version History

- **v1.4**: Current stable release with AI integration
- **v1.3**: Enhanced UI and reporting features
- **v1.2**: Added cloud synchronization
- **v1.0**: Initial release

## 🙏 Acknowledgments

- OpenAI for AI capabilities
- Flask community for web framework
- Contributors and testers

---

**Made with ❤️ by DXD Global**
