from getpass import getpass
from xmlrpc import client
from datetime import datetime, timedelta
import configparser


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
        # print(attendance['emp_id'])
        for key, value in enumerate(attendance.items()):
            print(key, ':', value[0], ':', value[1])
        if not read_only:
            sign_in_time = attendance['sign_in_time']
            sign_out_time = attendance['sign_out_time']
            if sign_in_time and sign_out_time:
                sign_in_time_dt = datetime.strptime(sign_in_time, dt_format) + time_delta
                sign_in_minute = 0
                sign_in_hour = sign_in_time_dt.hour
                if sign_in_hour >= 9:
                    if sign_in_time_dt.minute > 0:
                        sign_in_minute = 15
                    if sign_in_time_dt.minute > 15:
                        sign_in_minute = 30
                    if sign_in_time_dt.minute > 30:
                        sign_in_minute = 45
                    if sign_in_time_dt.minute > 45:
                        sign_in_hour += 1
                        sign_in_minute = 0
                else:
                    sign_in_hour = 9
                    sign_in_minute = 0
                updated_in_date = sign_in_time_dt.replace(minute=sign_in_minute, hour=sign_in_hour, second=0)

                sign_out_time_dt = datetime.strptime(sign_out_time, dt_format) + time_delta
                minute = 0
                hour = sign_out_time_dt.hour
                if hour < 18:
                    if sign_out_time_dt.minute > 0:
                        minute = 15
                    if sign_out_time_dt.minute > 15:
                        minute = 30
                    if sign_out_time_dt.minute > 30:
                        minute = 45
                    if sign_out_time_dt.minute > 45:
                        hour += 1
                        minute = 0
                else:
                    hour = 18
                    minute = 0
                updated_out_date = sign_out_time_dt.replace(minute=minute, hour=hour, second=0)
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


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')
    userName_param = config['DEFAULT']['username']
    empId_param = config['DEFAULT']['empid']
    from_date_param = config['DEFAULT']['from_date']
    to_date_param = config['DEFAULT']['to_date']
    readOnly_param = config['DEFAULT']['readonly']
    password_param = config['DEFAULT']['password']
    print(userName_param)
    print(empId_param)
    print(from_date_param)
    print(to_date_param)
    print(readOnly_param)
    print(password_param)
    if str(userName_param) != "" and str(empId_param) != "" and str(from_date_param) != ""\
            and str(to_date_param) != "" and str(readOnly_param) != "" and str(password_param) != "":
        update_attendance(str(userName_param), str(password_param), int(empId_param), str(from_date_param),
                          str(to_date_param), str(readOnly_param).lower() == 'true')
    else:
        print("Please check your config values.")
