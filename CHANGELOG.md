# DDS FocusPro - Changelog

## Version 1.7.0 (January 27, 2026)

### 🚀 **Major Features & Enhancements**

#### ☁️ **Contabo Object Storage Integration**
- **Dual Storage System**: Implemented Contabo Object Storage alongside AWS S3 for redundant backup
- **Screenshot Backup**: All screenshots now automatically upload to both AWS S3 and Contabo
- **Log Backup**: Session logs and activity data synchronized to Contabo storage
- **EU Region Storage**: Using `eu2.contabostorage.com` for European data compliance
- **S3-Compatible API**: Seamless integration using boto3 with S3-compatible endpoints

#### 🔐 **Storage Architecture**
- **Bucket Structure**: `focuspro` bucket with organized folder hierarchy
  - `users_screenshots/{date}/{email}/{task}/` - Screenshot organization
  - `users_logs/{date}/{email}/{task}/` - Log file organization
- **Automatic Failover**: Graceful error handling if either storage service is unavailable
- **Parallel Uploads**: Screenshots and logs upload simultaneously to both storage providers

### 🔧 **Technical Improvements**
- **Enhanced Reliability**: Dual storage ensures data persistence even if one service fails
- **Better Performance**: Optimized upload handling for multiple storage destinations
- **Improved Logging**: Detailed logging for Contabo operations and upload status

### 📁 **File Structure Updates**
- New functions in `moduller/s3_uploader.py`:
  - `upload_screenshot_to_contabo()` - Handle screenshot uploads
  - `upload_logs_to_contabo()` - Handle log file uploads
- Integration in `app.py` for automatic backup operations

### 🐛 **Bug Fixes**
- **Screenshot Interval Display**: Fixed issue where screenshot interval showed "N/A" in UI
  - Updated `/get_screenshot_time_interval` endpoint to properly return interval in minutes
  - Added fallback to config_manager when API unavailable or user not found
  - Fixed settings page to use correct API endpoint with proper payload
  - Changed hardcoded "5 minutes" value to dynamic loading
- **UI Version Updates**: Updated all UI pages (login, client, help, settings) to display v1.7.0

### 🐛 **Bug Fixes**
- Improved error handling for storage upload failures
- Better logging for troubleshooting upload issues

---

## Version 1.6.1 (January 2, 2026)
- Bug fixes and stability improvements
- Performance optimizations

---

## Version 1.5 (November 6, 2025)

### 🎯 **Major Features & Improvements**

#### 📸 **Screen Capture & Time Tracking Enhancements**
- **Custom Screenshot Intervals**: Admin can now set personalized screenshot intervals for each user
- **Meeting Screenshots**: Screenshots now continue capturing during meetings for complete workflow documentation
- **Total Logged Time System**: 
  - Introduces comprehensive time tracking that starts on user login
  - Continues running until user logout
  - Unaffected by idle states, meetings, or task status changes
  - Provides accurate total work time reporting
- **User Profile Integration**: User profile images now display on the main dashboard

#### 🤝 **Meeting Module Overhaul**
- **Mandatory Work Stop**: Users must stop active work before initiating meetings
- **Required Project Selection**: Project and task selection is now mandatory before meeting start
- **Meeting Notes Feature**: Added ability to capture detailed meeting notes at meeting conclusion
- **Timesheet Integration**: Meeting duration now appears in user timesheets for accurate time tracking
- **Smart Idle Management**: Idle tracking automatically disabled during meetings to prevent interruptions

#### 🎨 **Enhanced User Interface**
- **Redesigned Sidebar**: 
  - Removed redundant app name and unused navigation items
  - Now displays current active project, task, and due date information
  - Expandable task details on click for comprehensive task information
- **Theme System**: 
  - Added Dark Mode and Light Mode options
  - User-customizable interface preferences
- **Screenshot Interval Display**: Current screenshot interval now visible on main screen

### 🔧 **Technical Improvements**
- **Auto-Connector Startup**: Connector now starts automatically with desktop application
- **Silent Operation**: Connector runs silently without console window
- **Enhanced Error Handling**: Improved stability and error recovery
- **Process Management**: Better cleanup and process tracking

### 🚀 **Performance & Stability**
- **Memory Optimization**: Reduced memory footprint during operation
- **Faster Startup**: Improved application launch time
- **Better Resource Management**: Enhanced cleanup procedures for stable operation

### 🐛 **Bug Fixes**
- Fixed connector auto-startup issues
- Resolved PyInstaller compatibility problems
- Fixed flush_print function for silent operation
- Improved process detection and cleanup

---

## Version 1.4 (Previous Release)
- Basic time tracking functionality
- Screenshot capture system
- Task management interface
- Initial meeting support

---

## Version 1.3 (Previous Release)
- User authentication system
- Project management features
- Basic timesheet functionality

---

## Installation Notes

### System Requirements
- Windows 10 or later
- 4GB RAM minimum (8GB recommended)
- 500MB free disk space
- Internet connection for data synchronization

### Upgrade Instructions
1. Close any running DDS FocusPro instances
2. Run the new installer (DDSFocusProSetup-v1.5.exe)
3. Follow installation prompts
4. Your previous settings and data will be preserved

### What's New for Users
- **Improved Time Tracking**: More accurate logging with total time display
- **Better Meeting Management**: Streamlined meeting workflow with mandatory project selection
- **Enhanced UI**: Choose between Dark and Light modes for comfortable viewing
- **Smarter Screenshots**: Customizable intervals and meeting-aware capture

### What's New for Administrators
- **Per-User Screenshot Control**: Set individual screenshot intervals for each team member
- **Comprehensive Reporting**: Meeting durations now included in timesheet reports
- **Better Visibility**: User profile images on dashboard for easy identification

---

*For technical support or feature requests, please contact the DDS development team.*