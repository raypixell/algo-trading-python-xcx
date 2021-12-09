from flask import Flask,render_template,request,send_file
from datetime import datetime,timedelta
import pytz
import requests
from flask_socketio import SocketIO
import json
import os.path
from apscheduler.schedulers.background import BackgroundScheduler
import schedule
from commodities_gold import GoldCommodities
from commodities_silver import SilverCommodities
from commodities_natural_gas import NaturalGasCommodities
from commodities_lead import LeadCommodities

scheduler = BackgroundScheduler({'apscheduler.timezone': 'Asia/Calcutta'})
scheduler.start()



gold_job = None
silver_job = None
natural_gas_job = None
lead_job = None
stop_all_job = None

gold_log_report = None
silver_log_report = None
natural_gas_log_report = None
lead_log_report = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyzVIKASJHA'
socketio = SocketIO(app,logger=True, engineio_logger=True, cors_allowed_origins="*")
tz = pytz.timezone('Asia/Kolkata')

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'            
    elif request.method == 'GET':
        return render_template('index.html')

@app.route("/settings", methods=['POST', 'GET'])
def settings():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'
    elif request.method == 'GET':
        return render_template('settings.html')

@app.route("/download/<int:selectedCommodities>")
def download(selectedCommodities):
    if selectedCommodities == 1:
        now = datetime.now()
        now = now.astimezone(tz)
        gold_log_file_name = "gold_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        if os.path.exists(gold_log_file_name):
            return send_file(gold_log_file_name, as_attachment=True)
        else:
            return "No log found for Gold Commodities."
   
    elif selectedCommodities == 2:
        now = datetime.now()
        now = now.astimezone(tz)
        silver_log_file_name = "silver_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        if os.path.exists(silver_log_file_name):
            return send_file(silver_log_file_name, as_attachment=True)
        else:
            return "No log found for Silver Commodities."
        
    elif selectedCommodities == 3:
        now = datetime.now()
        now = now.astimezone(tz)
        natural_gas_log_file_name = "natural_gas_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        if os.path.exists(natural_gas_log_file_name):
            return send_file(natural_gas_log_file_name, as_attachment=True)
        else:
            return "No log found for Natural Gas Commodities."
        
    elif selectedCommodities == 4:
        now = datetime.now()
        now = now.astimezone(tz)
        lead_log_file_name = "lead_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        if os.path.exists(lead_log_file_name):
            return send_file(lead_log_file_name, as_attachment=True)
        else:
            return "No log found for Lead Commodities."
        
        
@socketio.on('connected')
def onConnected(data):
    print(str(data))
    print(request.sid)

def stopAllCommodities():
    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    # Stop Gold Script
    stopGoldCommodities(script_running_staus)

    # Stop Silver Script
    stopSilverCommodities(script_running_staus)

    # Stop Natural Gas Script
    stopNaturalGasCommodities(script_running_staus)

    # Stop Lead Script
    stopLeadCommodities(script_running_staus)

    stop_all_job.remove()


stop_all_job = scheduler.add_job(stopAllCommodities, trigger='cron', hour='23', minute='58',second='30',day='*')
        
@socketio.on('start_script')
def start_script(data):
    selectedCommodities = data['startScriptFor']
    selectedInterval = data['selectedInterval']
    intervalValue = int(data['intervalValue'])
    print('start script selected commodities : ' + str(selectedCommodities))
    print('start script selected candle interval : ' + selectedInterval)

    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if selectedCommodities == 1:
        goldCommodities = GoldCommodities(socketio,selectedInterval)
        goldCommodities.loginKite()

        script_running_staus["Gold"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global gold_job
        if intervalValue == 1:
            gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='gold')
        elif intervalValue == 2:
            gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/5',id='gold')
        elif intervalValue == 3:
            gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/10',id='gold')
        elif intervalValue == 4:
            gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/15',id='gold')
        elif intervalValue == 5:
            gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/30',id='gold')

    elif selectedCommodities == 2:
        silverCommodities = SilverCommodities(socketio,selectedInterval)
        silverCommodities.loginKite()

        script_running_staus["Silver"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global silver_job
        if intervalValue == 1:
            silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='silver')
        elif intervalValue == 2:
            silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/5',id='silver')
        elif intervalValue == 3:
            silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/10',id='silver')
        elif intervalValue == 4:
            silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/15',id='silver')
        elif intervalValue == 4:
            silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/30',id='silver')

    elif selectedCommodities == 3:
        naturalGasCommodities = NaturalGasCommodities(socketio,selectedInterval)
        naturalGasCommodities.loginKite()

        script_running_staus["NaturalGas"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global natural_gas_job
        if intervalValue == 1:
            natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='naturalgas')
        elif intervalValue == 2:
            natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/5',id='naturalgas')
        elif intervalValue == 3:
            natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/10',id='naturalgas')
        elif intervalValue == 4:
            natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/15',id='naturalgas')
        elif intervalValue == 5:
            natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/30',id='naturalgas')

    elif selectedCommodities == 4:
        leadCommodities = LeadCommodities(socketio,selectedInterval)
        leadCommodities.loginKite()

        script_running_staus["Lead"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)
        
        global lead_job
        if intervalValue == 1:
            lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='lead')
        elif intervalValue == 2:
            lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/5',id='lead')
        elif intervalValue == 3:
            lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/10',id='lead')
        elif intervalValue == 4:
            lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/15',id='lead')
        elif intervalValue == 5:
            lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*/30',id='lead')
        

@socketio.on('stop_script')
def stop_script(data):
    selectedCommodities = data['stopScriptFor']
    print('stop script btn clicked : ' + str(selectedCommodities))

    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if selectedCommodities == 1:
        stopGoldCommodities(script_running_staus)

    elif selectedCommodities == 2:
        stopSilverCommodities(script_running_staus)
        
    elif selectedCommodities == 3:
        stopNaturalGasCommodities(script_running_staus)

    elif selectedCommodities == 4:
        stopLeadCommodities(script_running_staus)

def stopGoldCommodities(script_running_staus):
    try:
        if gold_job is not None:
            gold_job.remove()

        now = datetime.now()
        now = now.astimezone(tz)
        gold_log_file_name = "gold_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        f=open(gold_log_file_name, "a+")
        logString = 'Script Stopped! at : ' + str(now)
        f.write('\n'+logString)
        logString = '---------------------------'
        f.write('\n'+logString)

        # close file stream
        f.close()
        
        # read the txt file and get content
        f=open(gold_log_file_name, "r")
        if f.mode == 'r':
            global gold_log_report
            gold_log_report =f.read()
            
        # close file stream
        f.close()

        logMessage = {"logReport" : gold_log_report,"selected_commodities":1}
        socketio.emit('log_report',logMessage)

        # Update Script Running Status
        script_running_staus["Gold"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)
    
    except Exception as ex:
        print(ex)

def stopSilverCommodities(script_running_staus):
    try:
        if silver_job is not None:
            silver_job.remove()

        now = datetime.now()
        now = now.astimezone(tz)
        silver_log_file_name = "silver_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        f=open(silver_log_file_name, "a+")
        logString = 'Script Stopped! at : ' + str(now)
        f.write('\n'+logString)
        logString = '---------------------------'
        f.write('\n'+logString)

        # close file stream
        f.close()
        
        # read the txt file and get content
        f=open(silver_log_file_name, "r")
        if f.mode == 'r':
            global silver_log_report
            silver_log_report =f.read()
            
        # close file stream
        f.close()

        logMessage = {"logReport" : silver_log_report,"selected_commodities":2}
        socketio.emit('log_report',logMessage)

        # Update Script Running Status
        script_running_staus["Silver"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

    except Exception as ex:
        print(ex)
    
def stopNaturalGasCommodities(script_running_staus):
    try:
        if natural_gas_job is not None:
            natural_gas_job.remove()

        now = datetime.now()
        now = now.astimezone(tz)
        natural_gas_log_file_name = "natural_gas_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        f=open(natural_gas_log_file_name, "a+")
        logString = 'Script Stopped! at : ' + str(now)
        f.write('\n'+logString)
        logString = '---------------------------'
        f.write('\n'+logString)

        # close file stream
        f.close()
        
        # read the txt file and get content
        f=open(natural_gas_log_file_name, "r")
        if f.mode == 'r':
            global natural_gas_log_report
            natural_gas_log_report =f.read()
            
        # close file stream
        f.close()

        logMessage = {"logReport" : natural_gas_log_report,"selected_commodities":3}
        socketio.emit('log_report',logMessage)

        # Update Script Running Status
        script_running_staus["NaturalGas"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

    except Exception as ex:
        print(ex)

def stopLeadCommodities(script_running_staus):
    try:
        if lead_job is not None:
            lead_job.remove()

        now = datetime.now()
        now = now.astimezone(tz)
        lead_log_file_name = "lead_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

        f=open(lead_log_file_name, "a+")
        logString = 'Script Stopped! at : ' + str(now)
        f.write('\n'+logString)
        logString = '---------------------------'
        f.write('\n'+logString)

        # close file stream
        f.close()
        
        # read the txt file and get content
        f=open(lead_log_file_name, "r")
        if f.mode == 'r':
            global lead_log_report
            lead_log_report =f.read()
            
        # close file stream
        f.close()

        logMessage = {"logReport" : lead_log_report,"selected_commodities":4}
        socketio.emit('log_report',logMessage)

        # Update Script Running Status
        script_running_staus["Lead"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

    except Exception as ex:
        print(ex)

@socketio.on('save_access_token')
def save_access_token():
    # Fetch Access-Token From Api
    # https://www.zigtap.com/zerodha/myaccesstoken.txt
    accessTokenUrl = 'https://www.zigtap.com/zerodha/myaccesstoken.txt'
    try:
        uResponse = requests.get(accessTokenUrl)
        access_token_fetched = uResponse.text
        print(access_token_fetched)
        access_token_json = { 'access_token' : access_token_fetched }

        # write accessToken to json file
        with open("access_token.json", "w") as outfile:
            json.dump(access_token_json, outfile)

        socketio.emit('access_token_updated',access_token_fetched)

    except requests.ConnectionError as ex:
        print(ex)

@socketio.on('commodities_change')
def commodities_change(data):
    selectedCommodities = data['selected_commodities']
    print('received selectedCommodities : ' + selectedCommodities)
    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    # Update Start Stop Btn State
    socketio.emit('update_btn_state',script_running_staus)

    if int(selectedCommodities) == 1:
        try:

            now = datetime.now()
            now = now.astimezone(tz)
            gold_log_file_name = "gold_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            # read the txt file and get content
            f=open(gold_log_file_name, "r")
            if f.mode == 'r':
                global gold_log_report
                gold_log_report =f.read()
        
            # close file stream
            f.close()

            logMessage = {"logReport" : gold_log_report,"selected_commodities":1}
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":1}
            socketio.emit('log_report',logMessage)
            print(ex)
            
    elif int(selectedCommodities) == 2:
        try:

            now = datetime.now()
            now = now.astimezone(tz)
            silver_log_file_name = "silver_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            # read the txt file and get content
            f=open(silver_log_file_name, "r")
            if f.mode == 'r':
                global silver_log_report
                silver_log_report =f.read()
        
            # close file stream
            f.close()

            logMessage = {"logReport" : silver_log_report,"selected_commodities":2}
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":2}
            socketio.emit('log_report',logMessage)
            print(ex)

    elif int(selectedCommodities) == 3:
        try:

            now = datetime.now()
            now = now.astimezone(tz)
            natural_gas_log_file_name = "natural_gas_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            # read the txt file and get content
            f=open(natural_gas_log_file_name, "r")
            if f.mode == 'r':
                global natural_gas_log_report
                natural_gas_log_report =f.read()
        
            # close file stream
            f.close()

            logMessage = {"logReport" : natural_gas_log_report,"selected_commodities":3}
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":3}
            socketio.emit('log_report',logMessage)
            print(ex)

    elif int(selectedCommodities) == 4:
        try:

            now = datetime.now()
            now = now.astimezone(tz)
            lead_log_file_name = "lead_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            # read the txt file and get content
            f=open(lead_log_file_name, "r")
            if f.mode == 'r':
                global lead_log_report
                lead_log_report =f.read()
        
            # close file stream
            f.close()

            logMessage = {"logReport" : lead_log_report,"selected_commodities":4}
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":4}
            socketio.emit('log_report',logMessage)
            print(ex)    

if __name__ == '__main__':
    socketio.run(app)
    