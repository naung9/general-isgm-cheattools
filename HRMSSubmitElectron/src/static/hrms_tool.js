class HtmlLogger {
    levels = [
        'all',
        'debug',
        'info',
        'warn',
        'error',
    ];

    getStyle(level, css = '') {
        if (css !== '') return '';
        if (level === 'warn') {
            return 'background-color: orange;';
        } else if (level === 'error') {
            return 'background-color: red;';
        } else {
            return '';
        }
    }

    constructor(consoleDom, level = 'info') {
        this.consoleDom = consoleDom;
        this.level = this.levels.indexOf(level);
        if (this.level < 0) {
            this.level = 2
        }
    }

    get logLevel() {
        return this.level;
    }

    set logLevel(level) {
        this.level = this.levels.indexOf(level);
        if (this.level < 0) {
            this.level = 2
        }
    }

    clear() {
        this.consoleDom.innerHTML = '';
    }

    log(options, messages) {
        let level;
        let asElement = '';
        let title = '';
        let cssClass = '';
        if (typeof options === 'object') {
            level = options['level'];
            asElement = options['asElement'];
            title = options['title'];
            if (options.hasOwnProperty('class')) {
                cssClass = options['class'];
            }
        } else {
            level = options;
        }
        let finalMessage = '';
        if (asElement.toLowerCase() === 'table') {
            finalMessage = `<h3>${title}</h3><table class="${cssClass}" style="${this.getStyle(level, cssClass)}">`;
            messages.forEach(message => {
                finalMessage += `<tr>${message.toString()}</tr>`;
            });
            finalMessage += '</table>';
        } else if (asElement.toLowerCase() === 'list') {
            finalMessage = `<h3>${title}</h3><ul class="${cssClass}" style="${this.getStyle(level, cssClass)}">`;
            messages.forEach(message => {
                finalMessage += `<li>${message.toString()}</li>`;
            });
            finalMessage += '</ul>';
        } else {
            finalMessage = `<p class="${cssClass}" style="${this.getStyle(level, cssClass)}">[${level}] `;
            messages.forEach(message => {
                finalMessage += `${message.toString()}, `;
            });
            finalMessage += '</p><hr>';
        }
        this.consoleDom.innerHTML += finalMessage;
    }

    debug(...message) {
        if (this.level <= 1) {
            this.log('debug', [...message]);
        }
    }

    debugWithOption(option, ...message) {
        if (this.level <= 1) {
            this.log({'level': 'debug', ...option}, [...message]);
        }
    }

    info(...message) {
        if (this.level <= 2) {
            this.log('info', [...message]);
        }
    }

    infoWithOption(option, ...message) {
        if (this.level <= 2) {
            this.log({'level': 'info', ...option}, [...message]);
        }
    }

    warn(...message) {
        if (this.level <= 3) {
            this.log('warn', [...message]);
        }
    }

    warnWithOption(option, ...message) {
        if (this.level <= 3) {
            this.log({'level': 'warn', ...option}, [...message]);
        }
    }

    error(...message) {
        if (this.level <= 4) {
            this.log('error', [...message]);
        }
    }

    errorWithOption(option, ...message) {
        if (this.level <= 4) {
            this.log({'level': 'error', ...option}, [...message]);
        }
    }
}

const logger = new HtmlLogger(document.getElementById('consoleOut'));
$('#clear').click((e) => {
    logger.clear();
});
$('#logLevel').change((e) => {
    logger.logLevel = $('#logLevel').val();
});

function submitAttendance(userName, password, empID, fromDate, toDate, desiredCheckIn, desiredCheckOut, readOnly = true, leaveDays, hasWFH = false, url = 'http://hrms.isgm.site') {
    let dbName = 'Attendance_V2';
    let attendanceModel = 'manual.attendance';
    let employee = 'hr.employee';
    let [checkInHours, checkInMinutes] = desiredCheckIn.split(':').map(val => parseInt(val));
    let [checkOutHours, checkOutMinutes] = desiredCheckOut.split(':').map(val => parseInt(val));
    logger.debug(checkInHours, checkInMinutes, checkOutHours, checkOutMinutes);
    logger.debug(userName, password, empID);
    $.xmlrpc({
        url: url + '/xmlrpc/2/common',
        methodName: 'authenticate',
        params: [dbName, userName, password, {}],
        success: (response, status, jqXHR) => {
            $.xmlrpc({
                url: url + '/xmlrpc/2/object',
                methodName: 'execute_kw',
                params: [dbName, response[0], password, attendanceModel, 'search_read', [[['emp_id', '=', parseInt(empID)], ['attendance_date', '>=', fromDate], ['attendance_date', '<=', toDate]]]],
                success: (attendanceData, status, jqXHR) => {
                    const time_delta = 23400000; // UTC +6:30
                    attendanceData[0].forEach(attendance => {
                        if (isWeekend(new Date(attendance['attendance_date'])) || leaveDays.indexOf(attendance['attendance_date']) !== -1) {
                            return;
                        }
                        let logs = [];
                        Object.keys(attendance).forEach(key => {
                            logs.push(`<td>${key}</td><td>${attendance[key]}</td>`);
                        });
                        logger.debugWithOption({asElement: 'table', title: attendance['attendance_date']}, ...logs);
                        if (!readOnly) {
                            let sign_in_time = attendance['sign_in_time'];
                            let sign_out_time = attendance['sign_out_time'];
                            let attendance_obj = {};
                            const successCallback = (updateData, status, jqXHR) => {
                                let updateLogs = [];
                                Object.keys(attendance_obj).forEach(key => {
                                    updateLogs.push(`<td>${key}</td><td>${attendance_obj[key]}</td>`);
                                });
                                logger.infoWithOption({
                                    title: `${attendance['attendance_date']} Updated`,
                                    asElement: 'table'
                                }, ...updateLogs);

                            };
                            const errorCallback = (jqXHR, status, error) => {
                                logger.error(error);
                            };
                            if (sign_in_time && sign_out_time) {
                                let sign_in_time_dt = new Date(sign_in_time);
                                sign_in_time_dt.setTime(sign_in_time_dt.getTime() + time_delta);
                                let sign_in_minute = sign_in_time_dt.getMinutes();
                                let sign_in_hour = sign_in_time_dt.getHours();
                                if (getTotalMinutes(sign_in_hour, sign_in_minute) >= getTotalMinutes(checkInHours, checkInMinutes)) {
                                    if (sign_in_minute > 0)
                                        sign_in_minute = 15;
                                    if (sign_in_minute > 15)
                                        sign_in_minute = 30;
                                    if (sign_in_minute > 30)
                                        sign_in_minute = 45;
                                    if (sign_in_minute > 45) {
                                        sign_in_hour += 1;
                                        sign_in_minute = 0;
                                    }
                                } else {
                                    sign_in_hour = checkInHours;
                                    sign_in_minute = checkInMinutes;
                                }
                                let updated_in_date = sign_in_time_dt;
                                updated_in_date.setHours(sign_in_hour);
                                updated_in_date.setMinutes(sign_in_minute);
                                updated_in_date.setSeconds(0);

                                let sign_out_time_dt = new Date(sign_out_time);
                                sign_out_time_dt.setTime(sign_out_time_dt.getTime() + time_delta);
                                let sign_out_minute = sign_out_time_dt.getMinutes();
                                let sign_out_hour = sign_out_time_dt.getHours();
                                if (getTotalMinutes(sign_out_hour, sign_out_minute) <= getTotalMinutes(checkOutHours, checkOutMinutes)) {
                                    if (sign_out_minute > 0)
                                        sign_out_minute = 15;
                                    if (sign_out_minute > 15)
                                        sign_out_minute = 30;
                                    if (sign_out_minute > 30)
                                        sign_out_minute = 45;
                                    if (sign_out_minute > 45) {
                                        sign_out_hour += 1;
                                        sign_out_minute = 0;
                                    }
                                } else {
                                    sign_out_hour = checkOutHours;
                                    sign_out_minute = checkOutMinutes;
                                }
                                let updated_out_date = sign_out_time_dt;
                                updated_out_date.setHours(sign_out_hour);
                                updated_out_date.setMinutes(sign_out_minute);
                                updated_out_date.setSeconds(0);
                                let manual_in = new Date(updated_in_date - time_delta);
                                let manual_out = new Date(updated_out_date - time_delta);
                                attendance_obj = {
                                    'check_in_data_for_calendar': dateTimeFormatter(updated_in_date),
                                    'manual_in': dateTimeFormatter(manual_in),
                                    'check_out_data_for_calendar': dateTimeFormatter(updated_out_date),
                                    'manual_out': dateTimeFormatter(manual_out),
                                    'check_out_normal': true,
                                    'check_in_normal': true,
                                    'project_id': 180,
                                    'reason_in': 'normal',
                                    'reason_out': 'normal',
                                };
                                saveToXMLRPC([attendance['id']], attendance_obj, url, dbName, response[0], password, attendanceModel, successCallback, errorCallback);
                            }else{
                                if (hasWFH) {
                                    const checkInDate = new Date(`${attendance['attendance_date']} ${desiredCheckIn}`);
                                    const checkOutDate = new Date(`${attendance['attendance_date']} ${desiredCheckOut}`);
                                    const manualInDate = new Date(checkInDate.getTime() - time_delta);
                                    const manualOutDate = new Date(checkOutDate.getTime() - time_delta);
                                    attendance_obj = {
                                        'check_in_data_for_calendar': dateTimeFormatter(checkInDate),
                                        'manual_in': dateTimeFormatter(manualInDate),
                                        'check_out_data_for_calendar': dateTimeFormatter(checkOutDate),
                                        'manual_out': dateTimeFormatter(manualOutDate),
                                        'check_out_normal': true,
                                        'check_in_normal': true,
                                        'project_id': 180,
                                        'reason_in': 'normal',
                                        'reason_out': 'normal',
                                    };
                                    saveToXMLRPC([attendance['id']], attendance_obj, url, dbName, response[0], password, attendanceModel, successCallback, errorCallback);
                                }
                            }
                        }
                    });
                },
                error: (jqXHR, status, error) => {
                    logger.error(error);
                }
            });
        },
        error: (jqXHR, status, error) => {
            logger.error(error);
        }
    });
}

function saveToXMLRPC(idList, obj, url, dbName, uid, password, modelName, successCallback, errorCallback) {
    $.xmlrpc({
        url: url + '/xmlrpc/2/object',
        methodName: 'execute_kw',
        params: [dbName, uid, password, modelName, 'write', [idList, obj]],
        success: successCallback,
        error: errorCallback
    });
}

function getTotalMinutes(hours, minutes) {
    return (hours * 60) + minutes;
}

function isWeekend(date) {
    return date.getDay() === 6 || date.getDay() === 0;
}

function dateTimeFormatter(date) {
    let hour = date.getHours();
    let minute = date.getMinutes();
    let seconds = date.getSeconds();
    let months = date.getMonth() + 1;
    let day = date.getDate();
    return `${date.getFullYear()}-${months > 9 ? months : '0' + months}-${day > 9 ? day : '0' + day} ${hour > 9 ? hour : '0' + hour}:${minute > 9 ? minute : '0' + minute}:${seconds > 9 ? seconds : '0' + seconds}`;
}

$('#submit').submit((e) => {
    e.preventDefault();

    const leaves = [];
    $('.leave').each(function () {
        leaves.push($(this).val());
    });
    submitAttendance($('#uName').val(), $('#password').val(), $('#empId').val(), $('#fromDate').val(), $('#toDate').val(), $('#checkIn').val(), $('#checkOut').val(), $('#readOnly').is(':checked'), leaves, $('#hasWFH').is(':checked'));
});
let lastLeaveNo = 0;
$('#addLeaveBtn').click(e => {
    $(`<tr id="leaveRow${lastLeaveNo}"><td><input class="leave" id="leave${lastLeaveNo}" type="date"></td><td><button type="button" class="leaveBtn" id="${lastLeaveNo}">Remove</button></td></tr>`).insertAfter('#leaves');
    lastLeaveNo++;
});
document.body.addEventListener('click', function (e) {
    if (e.target.className === 'leaveBtn') {
        $(`#leaveRow${e.target.id}`).remove();
    }
})
