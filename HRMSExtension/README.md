# HRMS Submit Tool Browser Extension

## Disclaimer
* The extension is not signed by firefox or chrome and can only be used at ISGM Office's network `Sijimusho`
* If you are using write mode, which is the main point of this extension, be careful to input the correct and valid data.
* We will not hold any responsibility for any critical errors and so use it at your own risk
* Even if we don't hold any responsibility, you are welcomed to contribute by reporting errors or creating pull requests

## Features
* Reading Attendance Data From HRMS Server
* Can read or change attendance between given `fromDate` and `toDate` and skip out weekends and leave days automatically
* Automatically add project, manual in, manual out, reason in , reason out, check in normal, check out normal properties to your attendance
* Supports html logging because chrome doesn't support logging for extensions in console
* Supports two mode (Read and Write)
* Read mode is for reading data from server
* Write mode is for reading and writing data to server

## Install
Clone this repository first with `git clone`
### Google Chrome
1. Go to Settings > Extensions or just enter `chrome://extensions/` in address bar
2. Enable Developer Mode
3. Load Unpacked and choose `cloned_repo_path/HRMSExtension/`
### Firefox
1. In the address bar, enter `about:debugging`
2. Click `This Firefox` link under the `Setup`
3. Click `Load Temporary Addon` and choose `cloned_repo_path/HRMSExtension/manifest.json`

## How to use
1. Fill in the necessary data and click submit.
2. It is recommended to use `Read Only` mode and log level `Debug` to view the read results and check if the results are as you desired.
3. To actually make changes to your attendance data, just do step 1 and uncheck the `Read Only` checkbox.
4. For users who are working from home partially or fully, it is necessary to check `Worked From Home` checkbox.
5. If you have taken any leave (full or half), please add your leave dates so that the plugin will skip making changes to those dates
6. For public holidays, please add the dates as leaves so the plugin will not make any changes to them.
