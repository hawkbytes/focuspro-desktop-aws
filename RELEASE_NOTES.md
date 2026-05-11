# DDS FocusPro v1.7.1 Release Notes

**Release Date**: February 2, 2026  
**Version**: 1.7.1  
**Build**: Stable Release

---

## 🎉 **What's New in v1.7.1**

### **Major Feature Updates**

#### 📸 **Latest Screenshot Preview**
- **Real-Time Preview**: View your most recently captured screenshot directly in the Settings page
- **Auto-Refresh**: Preview automatically updates every 30 seconds without page reload
- **Full-Size View**: Click to expand screenshot to full-size in modal overlay
- **Rich Metadata Display**:
  - Capture timestamp (local timezone)
  - Current project name
  - Current task name
  - Screenshot interval setting
  - File size information
- **Secure Access**: Users can only view their own screenshots
- **In-Memory Decryption**: Encrypted screenshots are decrypted securely without creating temporary files
- **Local-First**: Always loads from local filesystem, never requires cloud access
- **Performance Optimized**: 
  - In-memory caching for instant previews
  - Sub-500ms API response times
  - Minimal memory footprint

#### 🔄 **Technical Improvements**
- **Thread-Safe Cache Manager**: New singleton cache manager for screenshot metadata
- **Efficient File Lookup**: Smart filesystem scanning with automatic cache invalidation
- **API Endpoint**: New `/api/latest-screenshot` endpoint with base64 image streaming
- **Cache-First Strategy**: Optimized performance with in-memory caching
- **Graceful Error Handling**: User-friendly error messages and automatic recovery

### 🎨 **UI/UX Enhancements**
- **Settings Page Integration**: Seamlessly integrated into existing Settings page
- **Responsive Design**: Works perfectly on all screen sizes
- **Interactive Preview**: Hover effects and smooth transitions
- **Manual Refresh**: Refresh button for immediate updates
- **Loading States**: Clear loading indicators and status messages
- **Error States**: Helpful error messages with actionable guidance

### 🔒 **Security & Privacy**
- **User Isolation**: Users can only access their own screenshots
- **No Cloud Dependency**: Completely local file access
- **Encryption Support**: Full support for encrypted screenshot files
- **In-Memory Only**: Decryption happens in memory, no disk writes
- **Session-Based Auth**: Integrated with existing authentication system

---

## 🔄 **Upgrade Path from v1.7.0**

1. Close all running DDS FocusPro instances
2. Pull latest changes or install v1.7.1
3. Existing screenshots remain fully compatible
4. New screenshot preview feature available immediately in Settings page
5. No configuration changes required

---

## 📋 **What's Included in v1.7.1**

### All Features from v1.7.0 ✅
- Dual cloud storage (AWS S3 + Contabo)
- Enhanced screenshot capture system
- Meeting management
- Time tracking
- Activity monitoring
- AI-powered features
- **PLUS:** Latest Screenshot Preview feature

### New Files
- `moduller/screenshot_cache_manager.py` - Screenshot cache management
- `SCREENSHOT_PREVIEW_DOCUMENTATION.md` - Comprehensive technical documentation

### Modified Files
- `app.py` - Added `/api/latest-screenshot` endpoint and cache integration
- `templates/settings.html` - Added screenshot preview UI component
- `static/settings.css` - Added screenshot preview styles
- `version.py` - Updated to v1.7.1
- `RELEASE_NOTES.md` - This file

---

## 🐛 **Bug Fixes**
- Improved error handling in screenshot capture loop
- Better cache invalidation when files are deleted
- Fixed potential race conditions in cache updates
- Enhanced logging for troubleshooting

---

## 📊 **Performance Metrics**
- API Response Time: <500ms (p99)
- Cache Hit Rate: >95% (typical)
- Auto-Refresh Overhead: Minimal (1 request per 30s)
- Memory Usage: +1-2KB per active user

---

# DDS FocusPro v1.7.0 Release Notes

**Release Date**: January 27, 2026  
**Version**: 1.7.0  
**Build**: Stable Release

---

## 🎉 **What's New in v1.7.0**

### **Major Feature Updates**

#### ☁️ **Contabo Object Storage Integration**
- **Dual Cloud Storage**: Added Contabo Object Storage as a secondary backup alongside AWS S3
- **Enhanced Data Security**: All screenshots and logs now automatically backed up to two independent cloud providers
- **European Data Center**: Utilizing EU2 region (`eu2.contabostorage.com`) for GDPR compliance
- **S3-Compatible API**: Seamless integration using industry-standard S3 protocols via boto3

#### 🔄 **Redundant Backup System**
- **Parallel Uploads**: Data simultaneously uploaded to both AWS S3 and Contabo storage
- **Automatic Failover**: Continues operation even if one storage provider is unavailable
- **Organized Structure**:
  - Screenshots: `users_screenshots/{date}/{email}/{task}/`
  - Logs: `users_logs/{date}/{email}/{task}/`
- **Zero Data Loss**: Redundant storage ensures no data loss even during service outages

#### 🔐 **Enhanced Reliability**
- **Dual Storage Confirmation**: Both uploads verified before marking as successful
- **Improved Error Handling**: Graceful degradation if either storage service fails
- **Comprehensive Logging**: Detailed logs for troubleshooting upload operations
- **Storage Monitoring**: Real-time status updates for both storage backends

### 🔧 **Technical Improvements**
- **New Functions**: Added `upload_screenshot_to_contabo()` and `upload_logs_to_contabo()`
- **Optimized Uploads**: Efficient parallel upload handling
- **Better Performance**: Minimized upload latency with async operations
- **Clean Architecture**: Modular storage functions in `moduller/s3_uploader.py`

### 📦 **Storage Configuration**
- **Contabo Bucket**: `focuspro`
- **Contabo Region**: `eu2`
- **Contabo Endpoint**: `https://eu2.contabostorage.com`
- **AWS S3 Bucket**: `ddsfocustime` (unchanged)

### 🐛 **Bug Fixes**
- **Screenshot Interval Display Fix**: Resolved "N/A" display issue in UI
  - Fixed API endpoint to properly return screenshot interval in minutes
  - Added fallback to configuration file (1-minute default) when API unavailable
  - Updated settings page JavaScript to fetch interval from correct endpoint
  - Changed hardcoded values to dynamic loading from backend
- **UI Version Consistency**: Updated all pages to display correct v1.7.0 version number
- Fixed edge cases in storage upload error handling
- Improved logging for failed upload attempts
- Better error messages for troubleshooting storage issues

---

## 🔄 **Upgrade Path from v1.6.1**

1. Close all running DDS FocusPro instances
2. Install v1.7.0 using the new installer
3. Existing settings and data preserved automatically
4. New Contabo storage will activate automatically

---

## Version 1.6.1 (January 2, 2026)
- Bug fixes and stability improvements
- Performance optimizations

---

## Version 1.5 (November 6, 2025) - Legacy

### **Major Feature Updates**

#### 📸 **Smart Screen Capture System**
- **Personalized Screenshot Intervals**: Administrators can now set custom screenshot intervals for individual users
- **Meeting Continuity**: Screenshots continue during meetings to maintain complete workflow documentation
- **Enhanced Privacy**: Better control over when and how screenshots are captured

#### ⏱️ **Advanced Time Tracking**
- **Total Logged Time**: New comprehensive timer that tracks total work hours from login to logout
- **Persistent Tracking**: Time continues regardless of idle states, meetings, or task changes
- **Accurate Reporting**: More precise time calculations for payroll and productivity analysis

#### 🤝 **Professional Meeting Management**
- **Workflow Protection**: Users must stop active work before starting meetings
- **Mandatory Project Association**: All meetings require project and task selection
- **Meeting Documentation**: Add detailed notes at the end of each meeting
- **Timesheet Integration**: Meeting durations automatically appear in timesheet reports
- **Intelligent Idle Management**: Idle detection pauses during meetings

#### 🎨 **Modern User Experience**
- **Theme Selection**: Choose between elegant Dark Mode and clean Light Mode
- **Smart Sidebar**: Displays current project, task, and due date information
- **Interactive Task Details**: Click any task to expand full details and information
- **Live Settings Display**: Screenshot interval now visible on the main interface

#### 👤 **Enhanced User Profiles**
- **Dashboard Avatars**: User profile images now appear on the main dashboard
- **Better Identification**: Easier user recognition and management
- **Enhanced Process Management**: Automatic cleanup of old instances
- **Robust Path Resolution**: Works correctly in both development and production
- **Comprehensive Logging**: Detailed logs with UTF-8 support for all platforms

### 🔧 Technical Improvements
- **Unicode Compatibility**: Fixed all character encoding issues on Windows
- **PyInstaller Optimization**: Cleaner builds with excluded unnecessary dependencies
- **Error Handling**: Graceful handling of missing files and network issues
- **Background Processing**: Flask server runs in separate thread for responsiveness

### 📦 Build System
- **DDSFocusPro.exe**: 22.7 MB - Desktop GUI launcher
- **DDSFocusPro Connector.exe**: 44.5 MB - Backend Flask server
- **Automated Builds**: Single command builds both executables
- **Clean Architecture**: Separate .spec files for maintainable builds

### 🐛 Bug Fixes
- Fixed PIL import errors in connector executable
- Resolved Unicode logging crashes on Windows systems  
- Fixed template path resolution in PyInstaller bundles
- Corrected process cleanup and shutdown procedures
- Eliminated startup crashes due to missing dependencies

### 📋 Requirements
- Windows 10/11 (64-bit)
- No additional software required (all dependencies bundled)
- ~100MB disk space for both executables and logs

---

## Version 1.0 - Legacy (Previous)

### Features
- Single executable design
- Basic Flask backend
- Simple GUI interface
- Manual process management

### Known Issues (Fixed in 2.0)
- PIL dependency conflicts
- Unicode logging errors
- Path resolution problems
- Process cleanup issues
- Slow startup times

---

## Upgrade Instructions

### From Version 1.0 to 2.0
1. **Backup Data**: Save any important application data
2. **Clean Install**: Remove old executable and data
3. **New Installation**: Download both new executables
4. **Place Together**: Ensure both .exe files are in same folder
5. **Launch**: Run DDSFocusPro.exe (new GUI launcher)

### Migration Notes
- Application data format is compatible
- Settings may need to be reconfigured
- Log files will be recreated with new format
- Performance improvements should be immediately noticeable

---

## Development History

### 2025-09-28: Architecture Split
- Separated GUI and backend into independent executables
- Implemented robust process management
- Fixed all Unicode and path resolution issues
- Added comprehensive logging and error handling

### 2025-09-27: Initial Development
- Created single-executable Flask application
- Basic PyInstaller build system
- Initial GUI implementation with WebView
- Core functionality implementation

---

## Known Limitations

### Current Version (2.0)
- Windows-only support (cross-platform support planned)
- Requires both executables to be in same directory
- Flask server bound to localhost only
- Manual data backup required

### Planned Improvements
- Cross-platform support (Linux, macOS)
- Configurable server settings
- Automatic data backup and restore
- Plugin architecture for extensibility
- Web-based remote access option

---

## Support and Feedback

### Getting Help
1. Check USER_GUIDE.md for common solutions
2. Review log files in `logs/` directory
3. Try debug mode: `python desktop.py`
4. Report issues with detailed logs and system information

### Reporting Bugs
- Include application version and build date
- Provide relevant log files (desktop.log, flask.log)
- Describe steps to reproduce the issue
- Include system specifications (Windows version, RAM, etc.)

### Feature Requests
- Describe the desired functionality
- Explain the use case and benefits
- Consider implementation complexity
- Provide examples or mockups if applicable