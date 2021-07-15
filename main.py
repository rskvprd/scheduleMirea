import requests as rq
references = []


def get_references():
    """Download all .xlsx links from official MIREA website"""
    ref = 'http://mirea.ru/schedule'
    r = rq.get(ref)
    for line in r.text.split('\n'):
        if ('весна.xlsx' in line or 'осень.xlsx' in line or 'зима.xlsx' in line or 'лето.xlsx' in line) \
                and 'маг' not in line:
            for i in line.split('"'):
                if 'весна.xlsx' in i or 'осень.xlsx' in i or 'зима.xlsx' in i or 'лето.xlsx' in i:
                    references.append(i)


def download_schedule(ref):
    print('\nDownloading ' + ref.split('/')[-1])
    with open('resources/' + ref.split('/')[-1], 'bw') as file:
        file.write(rq.get(ref).content)


def find_groups():
    """Check groups in xlsx files to pair filename with groupname"""
    from re import match
    from pandas import read_excel
    from os import listdir, getcwd
    resources_dir = getcwd() + '/resources/'
    with open(resources_dir + 'group-department.txt', 'w', encoding='utf-8') as f:
        f.write('')
    for file in listdir(resources_dir):
        if 'весна.xlsx'in file or 'осень.xlsx' in file or 'зима.xlsx' in file or 'лето.xlsx' in file:
            print('\nReading' + resources_dir + file)
            try:
                data_frame = read_excel(resources_dir + file)
                with open(resources_dir + 'group-department.txt', 'a', encoding='utf-8') as f:
                    f.write('\n')
                    f.write('\n'.join([file + str(data_frame.iloc[0][j]) for j in range(len(data_frame.iloc[0]))
                                      if match(r'\w\w\w\w-\w\w-\w\w', str(data_frame.iloc[0][j]))]))
                del data_frame
            except Exception as e:
                print(e)


def init():
    get_references()
    for ref in references:
        download_schedule(ref)
    find_groups()
