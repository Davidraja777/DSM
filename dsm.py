import PySimpleGUI as sg
from datetime import datetime
import json
import pandas as pd
import calendar

# Users' login credentials
users = {
    'Mark': 'password1',
    'David': 'password2',
    'John': 'password3',
    'Andrew': 'password4'
}

# Define permissions for each user type
permissions = {
    'create': ['Mark', 'David'],
    'update_delivery_group': ['Mark', 'David'],
    'update_running_number': ['John', 'Andrew'],
    'update_tu_checkout': ['John', 'Andrew']
}

# Function to save a record to file
def add_record(user, delivery_group, tu_created, running_number, check_out):
    date = datetime.now()
    month, year = date.month, date.year
    filename = f"records_{month}_{year}.json"

    date_str = date.strftime("%Y-%m-%d %H:%M:%S")
    record = [date_str, user, delivery_group, tu_created, running_number, check_out, user, date_str]

    # Load existing records from the file
    try:
        with open(filename, 'r') as file:
            records = json.load(file)
    except FileNotFoundError:
        records = []
    except json.JSONDecodeError:
        sg.popup_error(f"Error reading records for {calendar.month_name[month]} {year}!", keep_on_top=True)
        records = []

    # Append the new record
    records.append(record)

    # Save records to the file
    with open(filename, 'w') as file:
        json.dump(records, file)

# Function To Save to Excel 
def save_to_excel(records, filename):
    headers = ['Date', 'Created By', 'Delivery Group', 'TU Created', 'Running Number', 'Check Out', 'Updated By', 'Update Time']
    df = pd.DataFrame(records, columns=headers)
    df.to_excel(filename, index=False)

# Login window
layout = [
    [sg.Text('Username:'), sg.Input(key='-USERNAME-')],
    [sg.Text('Password:'), sg.Input(key='-PASSWORD-', password_char='*')],
    [sg.Button('Login'), sg.Button('Exit')]
]

window = sg.Window('Login', layout)

user = None
while True:
    event, values = window.read()
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break
    if event == 'Login':
        username = values['-USERNAME-']
        password = values['-PASSWORD-']
        if username in users and users[username] == password:
            user = username
            sg.popup('Login Successful!')
            break
        else:
            sg.popup('Login Failed!')

window.close()

# Main window layout based on user permissions
delivery_group_input = sg.Input(key='-DELIVERY_GROUP-', size=(20, 1), disabled=(user not in permissions['update_delivery_group']))
tu_created_input = sg.Input(key='-TU_CREATED-', size=(20, 1), disabled=(user not in permissions['update_tu_checkout']))
running_number_input = sg.Input(key='-RUNNING_NUMBER-', size=(20, 1), disabled=(user not in permissions['update_running_number']))
check_out_input = sg.Input(key='-CHECK_OUT-', size=(20, 1), disabled=(user not in permissions['update_tu_checkout']))
add_record_button = sg.Button('Add Record', disabled=(user not in permissions['create']))
update_record_button = sg.Button('Update Record', disabled=(user not in permissions['update_tu_checkout']))

layout = [
    [sg.Text('User:', size=(25, 1)), sg.Text(user, size=(20, 1))],
    [sg.Text('Delivery Group Number:', size=(25, 1)), delivery_group_input],
    [sg.Text('TU Created:', size=(25, 1)), tu_created_input],
    [sg.Text('Running Number:', size=(25, 1)), running_number_input],
    [sg.Text('Check Out:', size=(25, 1)), check_out_input],
    [add_record_button, update_record_button, sg.Button('View Records'), sg.Button('Search By Delivery Group'), sg.Button('Exit')],
]

window = sg.Window('Record Keeper', layout, finalize=True, keep_on_top=True)
view_window = None
selected_record_to_edit = None

# Main event loop
while True:
    event, values = window.read()

    date = datetime.now()
    month, year = date.month, date.year
    filename = f"records_{month}_{year}.json"
    
    if event == sg.WINDOW_CLOSED or event == 'Exit':
        break

    if event == 'Add Record':
        # If the user is allowed to create a record
        if user in permissions['create']:
            add_record(user, values['-DELIVERY_GROUP-'], values['-TU_CREATED-'], values['-RUNNING_NUMBER-'], values['-CHECK_OUT-'])
            sg.popup('Record Added Successfully!', keep_on_top=True)

    if event == 'Search By Delivery Group':
        delivery_group_to_search = sg.popup_get_text('Enter Delivery Group Number:', title='Search By Delivery Group')
        if not delivery_group_to_search:
            continue
    
        # Load all records from all files
        records = []
        for year in range(2000, datetime.now().year + 1):  # Assuming records from the year 2000 onwards
            for month in range(1, 13):
                filename = f"records_{month}_{year}.json"
                try:
                    with open(filename, 'r') as file:
                        month_records = json.load(file)
                        records.extend(month_records)
                except FileNotFoundError:
                    continue
                except json.JSONDecodeError:
                    sg.popup_error(f"Error reading records for {calendar.month_name[month]} {year}!", keep_on_top=True)
                    continue
    
        # Filter records based on the provided Delivery Group number
        records = [record for record in records if record[2] == delivery_group_to_search]
    
        # Display the filtered records in the "View Records" window (same code as the 'View Records' event)
        headers = ['Date', 'Created By', 'Delivery Group', 'TU Created', 'Running Number', 'Check Out', 'Updated By', 'Time Updated']
        data = [[str(r[i]) for i in range(len(r))] for r in records]
        view_layout = [
            [sg.Table(values=data, headings=headers, display_row_numbers=False,
                auto_size_columns=True, num_rows=min(10, len(data)),
                justification='center', key='-TABLE-', enable_events=True,
                bind_return_key=True, select_mode=sg.TABLE_SELECT_MODE_EXTENDED)],
            [sg.Button('Edit', disabled=True), sg.Button('Select All'), sg.Button('Save To Excel'), sg.Button('Close')]
        ]
    
        if view_window:
            view_window.close()
        view_window = sg.Window('View Records', view_layout, keep_on_top=True, finalize=True)

    if event == 'View Records':
        # Get the start date from the user
        start_date_selected = sg.popup_get_date(title="Select Start Date", no_titlebar=True)
        if not start_date_selected:
            continue

        # Get the end date from the user
        end_date_selected = sg.popup_get_date(title="Select End Date", no_titlebar=True)
        if not end_date_selected:
            continue

        start_month, start_day, start_year = start_date_selected
        end_month, end_day, end_year = end_date_selected
    
        start_date_str = datetime(start_year, start_month, start_day).strftime("%Y-%m-%d")
        end_date_str = datetime(end_year, end_month, end_day).strftime("%Y-%m-%d")
    
        # Load records from the selected month's file
        records = []
        for year in range(start_year, end_year + 1):
            for month in range(start_month if year == start_year else 1, end_month + 1 if year == end_year else 13):
                filename = f"records_{month}_{year}.json"
                try:
                    with open(filename, 'r') as file:
                        month_records = json.load(file)
                        records.extend(month_records)
                except FileNotFoundError:
                    continue
                except json.JSONDecodeError:
                    sg.popup_error(f"Error reading records for {calendar.month_name[month]} {year}!", keep_on_top=True)
                    continue

    # Filter records based on the selected date range
    records = [record for record in records if start_date_str <= record[0].split(" ")[0] <= end_date_str]

    headers = ['Date', 'Created By', 'Delivery Group', 'TU Created', 'Running Number', 'Check Out', 'Updated By', 'Time Updated']
    data = [[str(r[i]) for i in range(len(r))] for r in records]
    view_layout = [
        [sg.Table(values=data, headings=headers, display_row_numbers=False,
            auto_size_columns=True, num_rows=min(10, len(data)),
            justification='center', key='-TABLE-', enable_events=True,
            bind_return_key=True, select_mode=sg.TABLE_SELECT_MODE_EXTENDED)],
        [sg.Button('Edit', disabled=True), sg.Button('Select All'), sg.Button('Save To Excel'), sg.Button('Close')]
    ]

    if view_window:
        view_window.close()
    view_window = sg.Window('View Records', view_layout, keep_on_top=True, finalize=True)

    while view_window:
        view_event, view_values = view_window.read()

        if view_event == sg.WINDOW_CLOSED or view_event == 'Close':
            view_window.close()
            view_window = None
            selected_record_to_edit = None
            break

        if view_event == '-TABLE-':
            # If a record was selected
            selected_record_to_edit = view_values['-TABLE-'][0]
            view_window['Edit'].update(disabled=False)

        if view_event == 'Edit' and view_values['-TABLE-']:
            selected_record_to_edit = view_values['-TABLE-'][0]
            record_to_edit = records[selected_record_to_edit]
            window['-DELIVERY_GROUP-'].update(record_to_edit[2])
            view_window.close()
            view_window = None
            selected_record_to_edit = None

        if view_event == 'Select All':
            view_window['-TABLE-'].update(select_rows=[i for i in range(len(data))])
            view_window['Edit'].update(disabled=False)

        if view_event == 'Save To Excel':
            filename = sg.popup_get_file('Save To Excel', save_as=True, default_extension=".xlsx", no_window=True, file_types=(("Excel Files", "*.xlsx"), ("All Files", "*.*")), keep_on_top=True)
            if filename:
                save_to_excel(records, filename)
                sg.popup('Records Saved Successfully!', keep_on_top=True)
    if view_window:
        view_window.close()

    if event == 'Update Record':
        # If the user is allowed to update a record
        if user in permissions['update_tu_checkout']:
            try:
                with open(filename, 'r') as file:
                    records = json.load(file)
            except FileNotFoundError:
                sg.popup_error(f"No records found for {calendar.month_name[month]} {year}!", keep_on_top=True)
                continue
            except json.JSONDecodeError:
                sg.popup_error(f"Error reading records for {calendar.month_name[month]} {year}!", keep_on_top=True)
                continue
            
            # Check if the record already exists
            delivery_group = values['-DELIVERY_GROUP-']
            existing_record = None
            for record in records:
                if record[2] == delivery_group:
                    existing_record = record
                    break
            
            if existing_record:
                # Update the existing record
                existing_record[3] = values['-TU_CREATED-']
                existing_record[4] = values['-RUNNING_NUMBER-']
                existing_record[5] = values['-CHECK_OUT-']
                existing_record[6] = user # Updated by
                existing_record[7] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # Update Time

                # Save the updated records to the file
                with open(filename, 'w') as file:
                    json.dump(records, file)
                sg.popup('Record Updated Successfully!', keep_on_top=True)
            else:
                sg.popup_error(f"No existing record found for Delivery Group: {delivery_group}!", keep_on_top=True)


window.close()
