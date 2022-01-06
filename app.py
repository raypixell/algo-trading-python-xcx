# Application Level Impots
from flask import Flask,render_template,request,send_file
from datetime import datetime,timedelta
import pytz
import requests
from flask_socketio import SocketIO
import json
import os.path
from threading import Thread

# Scripts Import
from commodities_gold import GoldCommodities
from commodities_silver import SilverCommodities
from commodities_natural_gas import NaturalGasCommodities
from commodities_lead import LeadCommodities
from bank_nifty import BankNifty
from nifty import Nifty


gold_job = None
silver_job = None
natural_gas_job = None
lead_job = None
bank_nifty_job = None
nitfy_job = None
stop_all_job = None

gold_log_report = None
silver_log_report = None
natural_gas_log_report = None
lead_log_report = None

goldCommodities = None
silverCommodities = None
naturalGasCommodities = None
leadCommodities = None
bankNifty = None
nifty = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyzVIKASJHA'
socketio = SocketIO(app,logger=True, engineio_logger=True, cors_allowed_origins="*",async_mode='gevent')
# socketio = SocketIO(app,logger=True, engineio_logger=True, cors_allowed_origins="*")
tz = pytz.timezone('Asia/Kolkata')

@app.route("/", methods=['POST', 'GET'])
def home():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'            
    elif request.method == 'GET':
        return render_template('home.html')


@app.route("/commodities", methods=['POST', 'GET'])
def commodities():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'            
    elif request.method == 'GET':
        return render_template('commodities.html')

@app.route("/nifty", methods=['POST', 'GET'])
def nifty():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'            
    elif request.method == 'GET':
        return render_template('nifty.html')

@app.route("/bank_nifty", methods=['POST', 'GET'])
def bank_nifty():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'            
    elif request.method == 'GET':
        return render_template('bank_nifty.html')

@app.route("/settings", methods=['POST', 'GET'])
def settings():
    if request.method == "POST":
        return 'POST METHOD EXECUTED'
    elif request.method == 'GET':
        return render_template('settings.html')

@socketio.on('connected')
def onConnected(msg):
    print('-------------')
    print(msg['data'])
    print('client connected with id : {}'.format(request.sid))
    print('------------')

    if msg['page'] == 2:
        # Connected to Nifty Page
        with open("nifty_script_running_status.json", "r") as jsonFile:
            script_running_staus = json.load(jsonFile)

            # Update Start Stop Btn State
            socketio.emit('update_btn_state_nifty',script_running_staus)
    
    elif msg['page'] == 3:
        # Connected to Bank Nifty Page
        with open("bank_nifty_script_running_status.json", "r") as jsonFile:
            script_running_staus = json.load(jsonFile)

            # Update Start Stop Btn State
            socketio.emit('update_btn_state_bank_nifty',script_running_staus)

# Commodities Script
@socketio.on('start_script')
def start_script(data):
    selectedCommodities = data['startScriptFor']
    intervalValue = int(data['intervalValue'])
    selectedInterval = data['selectedInterval']
    
    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if selectedCommodities == 1:
        global goldCommodities

        goldCommodities = GoldCommodities(socketio,selectedInterval)
        goldCommodities.loginKite()

        script_running_staus["Gold"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global gold_job
        if intervalValue == 1:
            gold_job = Thread(target = goldCommodities.startCommoditiesAlgo, args =(1,), daemon = False)
            gold_job.start()
        elif intervalValue == 2:
            gold_job = Thread(target = goldCommodities.startCommoditiesAlgo, args =(5,), daemon = False)
            gold_job.start()
        elif intervalValue == 3:
            gold_job = Thread(target = goldCommodities.startCommoditiesAlgo, args =(10,), daemon = False)
            gold_job.start()
        elif intervalValue == 4:
            gold_job = Thread(target = goldCommodities.startCommoditiesAlgo, args =(15,), daemon = False)
            gold_job.start()
        elif intervalValue == 5:
            gold_job = Thread(target = goldCommodities.startCommoditiesAlgo, args =(30,), daemon = False)
            gold_job.start()

    elif selectedCommodities == 2:
        global silverCommodities

        silverCommodities = SilverCommodities(socketio,selectedInterval)
        silverCommodities.loginKite()

        script_running_staus["Silver"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global silver_job
        if intervalValue == 1:
            silver_job = Thread(target = silverCommodities.startCommoditiesAlgo, args =(1,), daemon = False)
            silver_job.start()
        elif intervalValue == 2:
            silver_job = Thread(target = silverCommodities.startCommoditiesAlgo, args =(5,), daemon = False)
            silver_job.start()
        elif intervalValue == 3:
            silver_job = Thread(target = silverCommodities.startCommoditiesAlgo, args =(10,), daemon = False)
            silver_job.start()
        elif intervalValue == 4:
            silver_job = Thread(target = silverCommodities.startCommoditiesAlgo, args =(15,), daemon = False)
            silver_job.start()
        elif intervalValue == 4:
            silver_job = Thread(target = silverCommodities.startCommoditiesAlgo, args =(30,), daemon = False)
            silver_job.start()

    elif selectedCommodities == 3:
        global naturalGasCommodities

        naturalGasCommodities = NaturalGasCommodities(socketio,selectedInterval)
        naturalGasCommodities.loginKite()

        script_running_staus["NaturalGas"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global natural_gas_job
        if intervalValue == 1:
            natural_gas_job = Thread(target = naturalGasCommodities.startCommoditiesAlgo, args =(1,), daemon = False)
            natural_gas_job.start()
        elif intervalValue == 2:
            natural_gas_job = Thread(target = naturalGasCommodities.startCommoditiesAlgo, args =(5,), daemon = False)
            natural_gas_job.start()
        elif intervalValue == 3:
            natural_gas_job = Thread(target = naturalGasCommodities.startCommoditiesAlgo, args =(10,), daemon = False)
            natural_gas_job.start()
        elif intervalValue == 4:
            natural_gas_job = Thread(target = naturalGasCommodities.startCommoditiesAlgo, args =(15,), daemon = False)
            natural_gas_job.start()
        elif intervalValue == 5:
            natural_gas_job = Thread(target = naturalGasCommodities.startCommoditiesAlgo, args =(30,), daemon = False)
            natural_gas_job.start()

    elif selectedCommodities == 4:
        global leadCommodities

        leadCommodities = LeadCommodities(socketio,selectedInterval)
        leadCommodities.loginKite()

        script_running_staus["Lead"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)
        
        global lead_job
        if intervalValue == 1:
            lead_job = Thread(target = leadCommodities.startCommoditiesAlgo, args =(1,), daemon = False)
            lead_job.start()
        elif intervalValue == 2:
            lead_job = Thread(target = leadCommodities.startCommoditiesAlgo, args =(5,), daemon = False)
            lead_job.start()
        elif intervalValue == 3:
            lead_job = Thread(target = leadCommodities.startCommoditiesAlgo, args =(10,), daemon = False)
            lead_job.start()
        elif intervalValue == 4:
            lead_job = Thread(target = leadCommodities.startCommoditiesAlgo, args =(15,), daemon = False)
            lead_job.start()
        elif intervalValue == 5:
            lead_job = Thread(target = leadCommodities.startCommoditiesAlgo, args =(30,), daemon = False)
            lead_job.start()


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
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        gold_log_file_name = "gold_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(gold_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":1}
        socketio.emit('log_report',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":1}
        socketio.emit('log_report',logMessage)
        

        # close file stream
        f.close()

        # Update Script Running Status
        script_running_staus["Gold"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        # Stop This Thread
        if gold_job.is_alive():
            print('gold thread stopped!')
            goldCommodities.stopThread()
            
    except Exception as ex:
        print(ex)

def stopSilverCommodities(script_running_staus):
    try:
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        silver_log_file_name = "silver_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(silver_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":2}
        socketio.emit('log_report',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":2}
        socketio.emit('log_report',logMessage)
        
        # close file stream
        f.close()

        # Update Script Running Status
        script_running_staus["Silver"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        # Stop This Thread
        if silver_job.is_alive():
            print('silver thread stopped!')
            silverCommodities.stopThread()
            
    except Exception as ex:
        print(ex)
    
def stopNaturalGasCommodities(script_running_staus):
    try:
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        natural_gas_log_file_name = "natural_gas_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(natural_gas_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":3}
        socketio.emit('log_report',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":3}
        socketio.emit('log_report',logMessage)
        
        # close file stream
        f.close()
        
        # Update Script Running Status
        script_running_staus["NaturalGas"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        # Stop This Thread
        if natural_gas_job.is_alive(): 
            print('natural gas thread stopped!')
            naturalGasCommodities.stopThread()
            
    except Exception as ex:
        print(ex)

def stopLeadCommodities(script_running_staus):
    try:
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        lead_log_file_name = "lead_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(lead_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":4}
        socketio.emit('log_report',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString,"selected_commodities":4}
        socketio.emit('log_report',logMessage)
        
        # close file stream
        f.close()

        # Update Script Running Status
        script_running_staus["Lead"] = False
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        # Stop This Thread
        if lead_job.is_alive():
            print('lead thread stopped!')
            leadCommodities.stopThread()
            
    except Exception as ex:
        print(ex)

@app.route("/download/<int:selectedCommodities>")
def download(selectedCommodities):
    if selectedCommodities == 1:
        now = datetime.now()
        now = now.astimezone(tz)
        gold_log_file_name = "gold_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(gold_log_file_name):
            return send_file(gold_log_file_name, as_attachment=True)
        else:
            return "No log found for Gold Commodities."
   
    elif selectedCommodities == 2:
        now = datetime.now()
        now = now.astimezone(tz)
        silver_log_file_name = "silver_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(silver_log_file_name):
            return send_file(silver_log_file_name, as_attachment=True)
        else:
            return "No log found for Silver Commodities."
        
    elif selectedCommodities == 3:
        now = datetime.now()
        now = now.astimezone(tz)
        natural_gas_log_file_name = "natural_gas_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(natural_gas_log_file_name):
            return send_file(natural_gas_log_file_name, as_attachment=True)
        else:
            return "No log found for Natural Gas Commodities."
        
    elif selectedCommodities == 4:
        now = datetime.now()
        now = now.astimezone(tz)
        lead_log_file_name = "lead_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(lead_log_file_name):
            return send_file(lead_log_file_name, as_attachment=True)
        else:
            return "No log found for Lead Commodities."
    
    elif selectedCommodities == 5:
        now = datetime.now()
        now = now.astimezone(tz)
        nifty_log_file_name = "nifty_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(nifty_log_file_name):
            return send_file(nifty_log_file_name, as_attachment=True)
        else:
            return "No log found for Nifty."
    elif selectedCommodities == 6:
        now = datetime.now()
        now = now.astimezone(tz)
        bank_nifty_log_file_name = "bank_nifty_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        if os.path.exists(bank_nifty_log_file_name):
            return send_file(bank_nifty_log_file_name, as_attachment=True)
        else:
            return "No log found for Bank Nifty."

@socketio.on('save_access_token')
def save_access_token():

    # Fetch Access-Token From Api
    accessTokenUrl = 'https://www.zigtap.com/zerodha/myaccesstoken.txt'

    try:

        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'}
        uResponse = requests.get(accessTokenUrl , headers=headers)
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

            with open('commodities_script_running_status.json', 'r') as openfile:
                script_running_staus_json = json.load(openfile)
                goldScriptStatus = script_running_staus_json['Gold']

            if goldScriptStatus:
                logMessage = {"logReport" : '',"selected_commodities":1}
                socketio.emit('log_report',logMessage)
            else:
                logMessage = {"logReport" : '',"selected_commodities":1}
                socketio.emit('log_report',logMessage)

        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":1}
            socketio.emit('log_report',logMessage)
            print(ex)
            
    elif int(selectedCommodities) == 2:
        try:

            with open('commodities_script_running_status.json', 'r') as openfile:
                script_running_staus_json = json.load(openfile)
                silverScriptStatus = script_running_staus_json['Silver']

            if silverScriptStatus:
                logMessage = {"logReport" : '',"selected_commodities":2}
                socketio.emit('log_report',logMessage)
            else:
                logMessage = {"logReport" : '',"selected_commodities":2}
                socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":2}
            socketio.emit('log_report',logMessage)
            print(ex)

    elif int(selectedCommodities) == 3:
        try:

            with open('commodities_script_running_status.json', 'r') as openfile:
                script_running_staus_json = json.load(openfile)
                naturalGasScriptStatus = script_running_staus_json['NaturalGas']

            if naturalGasScriptStatus:
                logMessage = {"logReport" : '',"selected_commodities":3}
                socketio.emit('log_report',logMessage)
            else:
                logMessage = {"logReport" : '',"selected_commodities":3}
                socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":3}
            socketio.emit('log_report',logMessage)
            print(ex)

    elif int(selectedCommodities) == 4:
        try:

            with open('commodities_script_running_status.json', 'r') as openfile:
                script_running_staus_json = json.load(openfile)
                leadScriptStatus = script_running_staus_json['Lead']

            if leadScriptStatus:
                logMessage = {"logReport" : '',"selected_commodities":4}
                socketio.emit('log_report',logMessage)
            else:
                logMessage = {"logReport" : '',"selected_commodities":4}
                socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            logMessage = {"logReport" : "","selected_commodities":4}
            socketio.emit('log_report',logMessage)
            print(ex)

# Bank Nifty Script
@socketio.on('start_bank_nifty_script')
def start_bank_nifty_script(data):
    with open("bank_nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    script_running_staus["Bank_Nifty"] = True
    with open("bank_nifty_script_running_status.json", "w") as jsonFile:
        json.dump(script_running_staus, jsonFile)

    # Update Start Stop Btn State
    socketio.emit('update_btn_state_nifty',script_running_staus)

    # Start Bank Nifty Script
    global bankNifty
    selectedInterval = '5minute'

    bankNifty = BankNifty(socketio,selectedInterval)

    global bank_nifty_job
    bank_nifty_job = Thread(target = bankNifty.startBankNiftyAlgo, args =(5,), daemon = False)
    bank_nifty_job.start()
        
@socketio.on('stop_bank_nifty_script')
def stop_bank_nifty_script(data):
    
    try:

        with open("bank_nifty_script_running_status.json", "r") as jsonFile:
            script_running_staus = json.load(jsonFile)
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        nifty_log_file_name = "bank_nifty_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(nifty_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString}
        socketio.emit('log_report_bank_nifty',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString}
        socketio.emit('log_report_bank_nifty',logMessage)
        

        # close file stream
        f.close()

        # Update Script Running Status
        script_running_staus["Bank_Nifty"] = False
        with open("bank_nifty_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state_nifty',script_running_staus)

        # Stop This Thread
        if bank_nifty_job.is_alive():
            print('Bank Nifty thread stopped!')
            bankNifty.stopThread()
            
    except Exception as ex:
        print(ex)

# Nifty Script
@socketio.on('start_nifty_script')
def start_nifty_script(data):
    with open("nifty_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    script_running_staus["Nifty"] = True
    with open("nifty_script_running_status.json", "w") as jsonFile:
        json.dump(script_running_staus, jsonFile)

    # Update Start Stop Btn State
    socketio.emit('update_btn_state_nifty',script_running_staus)

    # Start Nifty Script
    global nifty
    selectedInterval = '5minute'

    nifty = Nifty(socketio,selectedInterval)

    global nifty_job
    nifty_job = Thread(target = nifty.startNiftyAlgo, args =(5,), daemon = False)
    nifty_job.start()
        
@socketio.on('stop_nifty_script')
def stop_nifty_script(data):
    
    try:

        with open("nifty_script_running_status.json", "r") as jsonFile:
            script_running_staus = json.load(jsonFile)
        
        now = datetime.now()
        now = now.astimezone(tz)
        currentTime ='%02d-%02d-%02d  %02d:%02d' % (now.day,now.month,now.year,now.hour,now.minute)
        nifty_log_file_name = "nifty_" + '%02d-%02d-%02d.txt' % (now.day,now.month,now.year)

        # open file stream
        f=open(nifty_log_file_name, "a+")

        logString = 'Script Stopped! at : ' + str(currentTime)
        f.write('\n'+logString)

        logMessage = {"logReport" : logString}
        socketio.emit('log_report_nifty',logMessage)
        
        logString = '---------------------------'
        f.write('\n'+logString)

        logMessage = {"logReport" : logString}
        socketio.emit('log_report_nifty',logMessage)
        

        # close file stream
        f.close()

        # Update Script Running Status
        script_running_staus["Nifty"] = False
        with open("nifty_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
            
        # Update Start Stop Btn State
        socketio.emit('update_btn_state_nifty',script_running_staus)

        # Stop This Thread
        if nifty_job.is_alive():
            print('Nifty thread stopped!')
            Nifty.stopThread()
            
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    socketio.run(app)
    