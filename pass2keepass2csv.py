#!/usr/bin/env python3

# Copyright 2019 Juan Orti Alcaine <jortialc@redhat.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


# Export all the entries in password-store https://www.passwordstore.org/
# to a CSV file ready to import in KeePass 2


import os
import csv
import argparse
from subprocess import check_output


def read_secret(folder, file):
    return check_output(['/usr/bin/pass', 'show', folder + os.sep + file])


def create_entry(folder, file):
    raw_secret = read_secret(folder, file).decode("utf-8")
    entry = dict(Group='',
                 Title='',
                 Username='',
                 Password='',
                 URL='',
                 Notes=''
                 )
    entry['Group'] = folder
    entry['Title'] = file
    lines = raw_secret.splitlines()
    if not lines:
        return entry
    entry['Password'] = lines[0]
    del lines[0]
    notes = []
    for line in lines:
        if line.lower().startswith('username:') or line.lower().startswith('user:'):
            entry['Username'] = line.split(':')[1]
            continue
        if line.startswith('URL:'):
            entry['URL'] = line.replace('URL: ', '')
            continue
        notes.append(line)
    entry['Notes'] = "\n".join(notes)
    return entry


def export_passwords(output_file):
    basedir = os.path.join(os.environ['HOME'], ".password-store")
    os.umask(0o0077)
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['Group', 'Title', 'Username', 'Password', 'URL', 'Notes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for root, dirs, files in os.walk(basedir):
            for file in files:
                if file.endswith(".gpg"):
                    writer.writerow(create_entry(root.replace(basedir + os.sep, ''),
                                                 file.replace('.gpg', '')))


def main():
    description = 'Export pass entries to a KeePass 2 CSV file.'
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('output_file', help='The CSV file to write to')
    args = parser.parse_args()
    output_file = args.output_file
    print("File to write:", output_file)
    export_passwords(output_file)
    print("Export finished")


if __name__ == '__main__':
    main()
