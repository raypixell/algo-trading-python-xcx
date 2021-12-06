from flask import Flask,render_template,request,send_file
from datetime import datetime,timedelta
from flask_socketio import SocketIO
import json
import os
from apscheduler.schedulers.background import BackgroundScheduler
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

gold_log_report = None
silver_log_report = None
natural_gas_log_report = None
lead_log_report = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abcdefghijklmnopqrstuvwxyzVIKASJHA'
socketio = SocketIO(app,logger=True, engineio_logger=True, cors_allowed_origins="*")

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
        
@socketio.on('connected')
def onConnected(data):
    print(str(data))
    print(request.sid)

@socketio.on('start_script')
def start_script(data):
    selectedCommodities = data['startScriptFor']
    print('start script btn clicked : ' + str(selectedCommodities))

    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if selectedCommodities == 1:
        goldCommodities = GoldCommodities(socketio)
        goldCommodities.loginKite()

        script_running_staus["Gold"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global gold_job
        gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='gold')

    elif selectedCommodities == 2:
        silverCommodities = SilverCommodities(socketio)
        silverCommodities.loginKite()

        script_running_staus["Silver"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global silver_job
        silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='silver')

    elif selectedCommodities == 3:
        naturalGasCommodities = NaturalGasCommodities(socketio)
        naturalGasCommodities.loginKite()

        script_running_staus["NaturalGas"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)
        
        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)

        global natural_gas_job
        natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='naturalgas')

    elif selectedCommodities == 4:
        leadCommodities = LeadCommodities(socketio)
        leadCommodities.loginKite()

        script_running_staus["Lead"] = True
        with open("commodities_script_running_status.json", "w") as jsonFile:
            json.dump(script_running_staus, jsonFile)

        # Update Start Stop Btn State
        socketio.emit('update_btn_state',script_running_staus)
        
        global lead_job
        lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='lead')
        

@socketio.on('stop_script')
def stop_script(data):
    selectedCommodities = data['stopScriptFor']
    print('stop script btn clicked : ' + str(selectedCommodities))

    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    if selectedCommodities == 1:
        
        try:

            if gold_job is not None:
                gold_job.remove()

            now = datetime.now()
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

    elif selectedCommodities == 2:
        
        try:

            if silver_job is not None:
                silver_job.remove()

            now = datetime.now()
            silver_log_file_name = "silver_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            f=open(silver_log_file_name, "a+")
            logString = 'Script Stopped! : '
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

    elif selectedCommodities == 3:

        try:

            if natural_gas_job is not None:
                natural_gas_job.remove()

            now = datetime.now()
            natural_gas_log_file_name = "natural_gas_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            f=open(natural_gas_log_file_name, "a+")
            logString = 'Script Stopped! : '
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

            logMessage = {"logReport" : natural_gas_log_report,"selected_commodities":2}
            socketio.emit('log_report',logMessage)

            # Update Script Running Status
            script_running_staus["NaturalGas"] = False
            with open("commodities_script_running_status.json", "w") as jsonFile:
                json.dump(script_running_staus, jsonFile)

            # Update Start Stop Btn State
            socketio.emit('update_btn_state',script_running_staus)

        except Exception as ex:
            print(ex)
    
    elif selectedCommodities == 4:
        try:

            if lead_job is not None:
                lead_job.remove()

            now = datetime.now()
            lead_log_file_name = "lead_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)

            f=open(lead_log_file_name, "a+")
            logString = 'Script Stopped! : '
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

            logMessage = {"logReport" : lead_log_report,"selected_commodities":2}
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
def save_access_token(data):
    accessToken = data['access_token']
    print('received access token : ' + accessToken)

    # write accessToken to json file
    with open("access_token.json", "w") as outfile:
        json.dump(data, outfile)

@socketio.on('download_log')
def download_log(data):

    selectedCommodities = int(data['selected_commodities'])

    if selectedCommodities == 1:
        # download gold_log_report.json
        print('download gold report executed')
        now = datetime.now()
        gold_log_file_name = "gold_" + '%s-%s-%s.txt' % (now.day,now.month,now.year)
        script_dir = os.path.dirname(__file__)
        abs_file_path = os.path.join(script_dir, gold_log_file_name)
        print(abs_file_path)
        send_file(abs_file_path, as_attachment=True)
    elif selectedCommodities == 2:
        # download silver_log_report.json
        print('download silver report executed')
    elif selectedCommodities == 3:
        # download natural_gas_log_report.json
        print('download natural gas report executed')
    elif selectedCommodities == 4:
        # download lead_log_report.json
        print('download lead report executed')


@socketio.on('browser_closed')
def browser_closed(data):
    print('browser closed : ' + str(data))


@socketio.on('commodities_change')
def commodities_change(data):
    selectedCommodities = data['selected_commodities']
    print('received selectedCommodities : ' + selectedCommodities)
    with open("commodities_script_running_status.json", "r") as jsonFile:
        script_running_staus = json.load(jsonFile)

    # Update Start Stop Btn State
    socketio.emit('update_btn_state',script_running_staus)

    if int(selectedCommodities) == 1:
        # Now check if previous log report present or not
        try:

            now = datetime.now()
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
        # Now check if previous log report present or not
        try:

            now = datetime.now()
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
        # Now check if previous log report present or not
        try:

            now = datetime.now()
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
        # Now check if previous log report present or not
        try:

            now = datetime.now()
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
            logMessage = {"logReport" : "","selected_commodities":3}
            socketio.emit('log_report',logMessage)
            print(ex)    

if __name__ == '__main__':
    socketio.run(app)