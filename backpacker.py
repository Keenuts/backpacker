#!/bin/python3

import sys
import json
import datetime
import logging
import subprocess
import smtplib    
from email.mime.text import MIMEText

MAIL_OBJ='[NAS] Backup failed'
MAIL_BODY='Sample body'
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

def save(config, filename, src, dst):
    logging.info("Saving the directory: %s" % src);
    subprocess.call(["tar", "-cf", "/tmp/" + src, filename]);
    return subprocess.Popen(['scp', "/tmp/" + src, dst])
   
def load_config():
    try:
        f = open("config.json", "r");
        config = json.loads(f.read());
        f.close();
        return config;
    except json.decoder.JSONDecodeError as err:
        logging.error("Unable to parse config: %s" % str(err));
    except:
        logging.error("Missing fields in the config file.");
    return False

def send_email(config):
    msg = MIMEText(MAIL_BODY);
    msg['Subject'] = MAIL_OBJ
    msg['From'] = config['mail-from']
    msg['To'] = config['mail-to']
    try:
        s = smtplib.SMTP(config['mail-smtp'])
        s.sendmail(msg['From'], msg['To'], msg.as_string());
        s.quit();
    except:
        logging.error("Unable to send a report email.");


def process():
    config = load_config()
    if config == False:
        return False;
    try:
        processes = []
        today = datetime.datetime.now();

        f = open("save.json", "r");
        data = json.loads(f.read());
        f.close();

        for i in range(0, len(data['tasks'])):
            t = data['tasks'][i]
            if not check_valid(t):
                return False;

            last_save = get_date(t["last_save"]);
            directory = t["directory"]
            period = t["period"]

            delta = today - last_save;

            if  ((period == 'year' and delta.week >= 365) or
                (period == 'month' and delta.days >= 30) or
                (period == 'week' and delta.days >= 7) or
                (period == 'day' and delta.days >= 1)):


                src=directory + ".tar.gz"
                filename=directory + "_" + today.strftime("%Y-%m-%d") + ".tar.gz"
                dst=config['ssh-host'] + ":" + config['remote-dir'] + "/" + filename

                proc = save(config, directory, src, dst);
                processes.append((proc, i, src, dst)); 

        error = False
        for p in processes:
            print("Waiting for the file: " + p[2])
            p[0].wait()
            if p[0].returncode != 0:
                logging.error("Unable to copy %s to %s", p[2], p[3]);
                error = True
            else:
                data['tasks'][p[1]]['last_save'] = today.strftime("%Y-%m-%d")

        f = open("save.json", "w+");
        f.write(json.dumps(data, indent=4));
        f.close();

        if error:
            send_email(config);
        logging.info("Backup done.")
        return error != True;

    except json.decoder.JSONDecodeError as err:
        logging.error("Unable to parse save file: %s" % str(err));
        return False
    return True

exit(process())
