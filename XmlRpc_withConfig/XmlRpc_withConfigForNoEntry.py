from getpass import getpass
from xmlrpc import client
from datetime import datetime, timedelta
import configparser
import holidays

custom_holidays = holidays.HolidayBase()
# myanmar public holidays and leave days between start and end dates
custom_holidays.append(['2020-03-27', '2020-04-13', '2020-04-14', '2020-04-15', '2020-04-16',
                        '2020-04-17', '2020-05-01', '2020-05-06'])


def weekend_check(date_time_param):
    weekno = date_time_param.weekday()
    if weekno < 5:
        return False
    else:
        return True


def update_attendance(user_name: str, password: str, emp_id: int, from_date: str, to_date: str, read_only: bool):
    url = 'http://hrms.isgm.site'
    db_name = 'Attendance_V2'
    attendance_model = 'manual.attendance'
    employee = 'hr.employee'
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db_name, user_name, password, {})
    print(uid)
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    my_attendances = models.execute_kw(db_name, uid, password, attendance_model, 'search_read',
                                       [[['emp_id', '=', emp_id], ['attendance_date', '>=', from_date],
                                         ['attendance_date', '<=', to_date]]])
    time_delta = timedelta(hours=6, minutes=30)
    dt_format = '%Y-%m-%d %H:%M:%S'
    for attendance in my_attendances:
        print(attendance['emp_id'])
        for key, value in enumerate(attendance.items()):
            print(key, ':', value[0], ':', value[1])
        if not read_only:
            attendance_date = datetime.strptime(attendance['attendance_date']+" 00:00:00", dt_format)
            if not weekend_check(attendance_date) and attendance_date not in custom_holidays:
                sign_in_out_time_dt = attendance_date + time_delta
                updated_in_date = sign_in_out_time_dt.replace(minute=0, hour=9, second=0)
                updated_out_date = sign_in_out_time_dt.replace(minute=0, hour=18, second=0)
                print(str(updated_in_date))
                print(str(updated_out_date))
                attendance_obj = {
                    'check_in_data_for_calendar': str(updated_in_date),
                    'manual_in': str(updated_in_date - time_delta),
                    'check_out_data_for_calendar': str(updated_out_date),
                    'manual_out': str(updated_out_date - time_delta),
                    'check_out_normal': True,
                    'check_in_normal': True,
                    'project_id': 180,
                    'reason_in': 'normal',
                    'reason_out': 'normal',
                }
                print(models.execute_kw(db_name, uid, password, attendance_model,
                                        'write', [[attendance['id']], attendance_obj]))

    print('-------------- End ----------------')


def date_validate(date_text):
    try:
        datetime.strptime(date_text, '%Y-%m-%d')
        return True
    except ValueError:
        # raise
        print("Please check your date format. Date format must be 'yyyy-MM-dd' format.")
        exit()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    userName_param = config['DEFAULT']['username'] if config.has_option('DEFAULT', 'username') else ""

    empId_param = config['DEFAULT']['empid'] if config.has_option('DEFAULT', 'empid') else ""
    from_date_param = config['DEFAULT']['from_date'] if config.has_option('DEFAULT', 'from_date') else ""
    to_date_param = config['DEFAULT']['to_date'] if config.has_option('DEFAULT', 'to_date') else ""
    readOnly_param = config['DEFAULT']['readonly'] if config.has_option('DEFAULT', 'readonly') else ""
    password_param = config['DEFAULT']['password'] if config.has_option('DEFAULT', 'password') else ""
    print(userName_param)
    print(empId_param)
    print(from_date_param)
    print(to_date_param)
    print(readOnly_param)
    print(password_param)
    if str(userName_param) != "" and str(empId_param) != "" and str(from_date_param) != "" \
            and str(to_date_param) != "" and str(readOnly_param) != "" and str(password_param) != "" \
            and empId_param.isdigit() and date_validate(from_date_param) and date_validate(to_date_param):
        update_attendance(str(userName_param), str(password_param), int(empId_param), str(from_date_param),
                          str(to_date_param), str(readOnly_param).lower() == 'true')
    else:
        print("Please check your config values.")
