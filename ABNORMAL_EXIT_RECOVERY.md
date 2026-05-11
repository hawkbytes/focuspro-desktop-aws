# Abnormal Exit Detection and Recovery System

## Overview
This system automatically detects when the DDS Focus Pro application closes abnormally (due to power failure, internet disconnect, system crash, or forced shutdown) and saves a note to the database indicating the abnormal closure.

## How It Works

### 1. Session Tracking
When a user starts a task timer, the application creates a session file:
- **Location**: `data/current_session.json`
- **Contents**: Email, staff_id, task_id, task name, start time, is_meeting flag

### 2. Normal Exit
When the user properly stops the timer or logs out:
- The session file is deleted
- Task end time is recorded normally in the database

### 3. Abnormal Exit Detection
On application startup, the system:
1. Checks if `current_session.json` exists
2. If found, it means the previous session didn't close properly
3. Reads the session data (email, task_id, staff_id, start_time)
4. Creates an abnormal exit note
5. Updates the database with the note
6. Cleans up the session file

### 4. Database Update
The abnormal exit note is saved using the same pattern as meeting notes:
- **Table**: `tbltaskstimers`
- **Field**: `note`
- **Method**: Appends to existing note (if any) using CONCAT
- **Format**: 
```
⚠️ Application closed abnormally.
Possible causes: Internet disconnect, power failure, system crash, or forced shutdown.
```

## Implementation Details

### Function: `check_and_recover_abnormal_exit()`
**Location**: `app.py` (lines ~378-480)

**Process**:
1. Check for `data/current_session.json`
2. If not found → Normal startup
3. If found:
   - Read session data
   - Calculate end_time (current timestamp)
   - Create abnormal exit note
   - Connect to database
   - Execute UPDATE query:
     ```sql
     UPDATE tbltaskstimers 
     SET end_time = %s, 
         note = CONCAT(COALESCE(note, ''), '\n\n', %s)
     WHERE task_id = %s 
     AND staff_id = %s 
     AND end_time IS NULL
     ORDER BY start_time DESC
     LIMIT 1
     ```
   - Clean up session file
   - Close database connection

### When It Runs
- **Trigger**: Every time the Flask application starts (app.py line ~484)
- **Timing**: Before any routes are initialized
- **Output**: Console messages showing detection and database update status

## Testing
To test the abnormal exit detection:

1. Create a test session file:
```json
{
  "email": "test@example.com",
  "username": "Test User",
  "staff_id": 123,
  "start_time": "2025-01-15 10:00:00",
  "task": "Test Task",
  "task_id": 999,
  "is_meeting": false
}
```

2. Save to: `data/current_session.json`

3. Start the application (connector.exe or desktop.py)

4. Check console output for:
```
⚠️ ABNORMAL EXIT DETECTED!
✅ Abnormal exit note saved to database for task 999
Session file cleaned up
```

5. Verify in database:
```sql
SELECT note FROM tbltaskstimers 
WHERE task_id = 999 AND staff_id = 123
ORDER BY start_time DESC LIMIT 1;
```

## Integration Points

### Session File Creation
**Location**: `app.py` line ~1797
**Endpoint**: `/start_task_session`
```python
with open("data/current_session.json", "w", encoding="utf-8") as f:
    json.dump(session_data, f, indent=2)
```

### Session File Deletion (Normal Exit)
**Location**: `app.py` line ~2093
**Endpoint**: `/end_task_session`
```python
session_file = "data/current_session.json"
if os.path.exists(session_file):
    os.remove(session_file)
```

## Benefits
1. **No Data Loss**: Even if the app crashes, work time is recorded
2. **Transparency**: Users and admins can see when abnormal exits occurred
3. **Simple Implementation**: Uses existing database schema (note field)
4. **Automatic**: No user action required
5. **Follows Existing Pattern**: Uses same approach as meeting notes

## Future Enhancements (Optional)
- Add timestamp of abnormal exit detection
- Track crash frequency per user
- Send email notifications for repeated crashes
- Differentiate between crash types (power vs network vs force close)

## Related Files
- `app.py`: Main implementation (lines 378-484)
- `data/current_session.json`: Session tracking file
- `desktop.py`: Ensures session file is deleted on normal GUI close
- `moduller/veritabani_yoneticisi.py`: Database connection management

## Database Schema
**Table**: `tbltaskstimers`
- `id` (PRIMARY KEY)
- `task_id` (FOREIGN KEY)
- `staff_id` (FOREIGN KEY)
- `start_time` (DATETIME)
- `end_time` (DATETIME)
- `note` (TEXT) ← Abnormal exit messages saved here
- `hourly_rate` (DECIMAL)
