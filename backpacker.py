#!/bin/python3

import sys
import json
import datetime
import logging
import subprocess
import smtplib    
from email.mime.text import MIMEText

MAIL_FROM='from@test.test'
MAIL_TO='to@test.test'
MAIL_SMTP='smtp.test.com'
MAIL_OBJ='[NAS] Backup failed'
LOG_PATH="./"

logging.basicConfig(filename=LOG_PATH+'LOGS',
                    format='[%(asctime)s][%(levelname)s] %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.INFO);
logging.info("Starting backup.")

def check_valid(t):
    if not "directory" in t:
        logging.error("JSON incorrect: missing 'directory' field")
    elif not "period" in t:
        logging.error("JSON incorrect: missing 'period' field")
    elif not "last_save" in t:
        logging.error("JSON incorrect: missing 'last_save' field")
    else:
        if (
            t["period"] != 'year'
            and t["period"] != 'month'
            and t["period"] != 'week'
            and t["period"] != 'day'
            ):
            logging.error("Invalid period %s" % t["period"])
            return False
        return True
    return False

def get_date(data):
    if data == "unknown":
        return datetime.datetime.strptime("1970", "%Y");
    return datetime.datetime.strptime(data, "%Y-%m-%d");

def save(config, directory, date, process):
    logging.info("Saving the directory: %s" % directory);
    filename = directory + "_" + date + ".tar.gz"
    subprocess.call(["tar", "-cf", "/tmp/" + filename, directory + "/"]);
    args = filename, subprocess.Popen(['scp', "/tmp/" + filename, config['ssh-host']+ ":"])
    process.append(args)
   
def load_config():
    try:
        f = open("config.json", "r");
        config = json.loads(f.read());
        f.close();

        if not "ssh-host" in config:
            return False;
        if not "save-to-keep" in config:
            return False;
        return config;

    except json.decoder.JSONDecodeError as err:
        logging.error("Unable to parse config: %s" % str(err));

def send_email():
    msg = MIMEText(MAIL_BODY);
    msg['Subject'] = MAIL_OBJ
    msg['From'] = MAIL_FROM
    msg['To'] = MAIL_TO
    try:
        s = smtplib.SMTP(MAIL_SMTP)
        s.sendmail(msg['From'], msg['To'], msg.as_string());
        s.quit();
    except:
        logging.error("Unable to send a report email.");


def process():
    config = load_config()
    if config == False:
        return False;
    try:
        f = open("save.json", "r");
        data = json.loads(f.read());
        f.close();
        processes = []

        for t in data["tasks"]:
            if not check_valid(t):
                return False;

            last_save = get_date(t["last_save"]);
            directory = t["directory"]
            period = t["period"]

            today = datetime.datetime.now();
            delta = today - last_save;

            if (
                (period == 'year' and delta.week >= 365) or
                (period == 'month' and delta.days >= 30) or
                (period == 'week' and delta.days >= 7) or
                (period == 'day' and delta.days >= 1)
                ):
                save(config, directory, today.strftime("%Y-%m-%d"), processes);
                last_save = today
            t['last_save'] = last_save.strftime('%Y-%m-%d')

        error = False
        for p in processes:
            print("Waiting for the file: " + p[0])
            p[1].wait()
            if p[1].returncode != 0:
                logging.error("Unable to transfer the file %s" % p[0]);
                error = True

        f = open("save.json", "w+");
        f.write(json.dumps(data, indent=4));
        f.close();
        return error == True

    except json.decoder.JSONDecodeError as err:
        logging.error("Unable to parse save file: %s" % str(err));
        return False
    return True

if process() != 0:
    send_email();

logging.info("Backup done.")
