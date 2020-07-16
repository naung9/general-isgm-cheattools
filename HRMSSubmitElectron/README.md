# HRMS Submit Tool Browser Extension

## Disclaimer
* This application can only be used at ISGM Office's network `Sijimusho`
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
### Linux
> sudo snap install hrms-submit-tool --beta

## How to use
1. Fill in the necessary data and click submit.
2. It is recommended to use `Read Only` mode and log level `Debug` at first to view the read results and check if the results are as you desired.
3. To actually make changes to your attendance data, just do step 1 and uncheck the `Read Only` checkbox.
4. For users who are working from home partially or fully, it is necessary to check `Worked From Home` checkbox.
5. You can bypass the 15 minutes auto filling by checking `Bypass 15 minute check` box
6. If you have taken any leave (full or half), please add your leave dates so that the plugin will skip making changes to those dates
7. For public holidays, please add the dates as leaves so the plugin will not make any changes to them.
8. Be very careful about `Employee ID` field. It does not mean your employee ID which usually starts with 00. e.g 000202. It means the literal primary key from employee table.
9. You can obtain your employee id by visiting to Employee tab at [HRMS](http://hrms.isgm.site), find your employee info, click your info card and when you are at your employee detail page, you can get your id at the address bar with the key `id`
