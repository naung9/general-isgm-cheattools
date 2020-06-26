from getpass import getpass
from xmlrpc import client
from datetime import datetime, timedelta
import argparse


def update_attendance(user_name: str, password: str, emp_id: int, from_date: str, to_date: str, read_only: bool):
    print("read only ? {}".format(read_only))
    url = 'http://hrms.isgm.site'
    db_name = 'Attendance_V2'
    attendance_model = 'manual.attendance'
    employee = 'hr.employee'
    common = client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db_name, user_name, password, {})
    print('Auth ID : {}'.format(uid))
    models = client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    my_attendances = models.execute_kw(db_name, uid, password, attendance_model, 'search_read',
                                      [[['emp_id', '=', emp_id], ['attendance_date', '>=', from_date], ['attendance_date', '<=', to_date]]])
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
                print(attendance_obj)
#                print(models.execute_kw(db_name, uid, password, attendance_model,
#                                        'write', [[attendance['id']], attendance_obj]))
    print('-------------- End ----------------')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--username', required=True, help="User Name Of HRMS", type=str)
    parser.add_argument('--empid', help="Employee ID Of HRMS", type=int, default=1273)
    parser.add_argument('--from_date', required=True, help='From Date in yyyy-MM-dd format', type=str)
    parser.add_argument('--to_date', default=str(datetime.now().date()), help='To Date in yyyy-MM-dd format', type=str)
    parser.add_argument('--readonly', help="To Enable Readonly Mode. Default is true", choices=['True', 'False', 'true', 'false', 'TRUE', 'FALSE'], type=str, default='true')
    pwd = getpass(prompt='Type Password')
    args = parser.parse_args()
    print(args)
    update_attendance(args.username, pwd, args.empid, args.from_date, args.to_date, args.readonly.lower() == 'true')
