from flask import Flask,render_template,request
from flask_socketio import SocketIO
import json
from apscheduler.schedulers.background import BackgroundScheduler
from commodities_gold import GoldCommodities
from commodities_silver import SilverCommodities
from commodities_natural_gas import NaturalGasCommodities
from commodities_lead import LeadCommodities

scheduler = BackgroundScheduler()
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


@socketio.on('start_script')
def start_script(data):
    selectedCommodities = data['startScriptFor']
    print('start script btn clicked : ' + str(selectedCommodities))
    
    if selectedCommodities == 1:
        goldCommodities = GoldCommodities(socketio)
        goldCommodities.loginKite()

        global gold_job

        gold_job = scheduler.add_job(goldCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='gold')
        scheduler.start()
    elif selectedCommodities == 2:
        silverCommodities = SilverCommodities(socketio)
        silverCommodities.loginKite()

        global silver_job

        silver_job = scheduler.add_job(silverCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='silver')
        scheduler.start()


    elif selectedCommodities == 3:
        naturalGasCommodities = NaturalGasCommodities(socketio)
        naturalGasCommodities.loginKite()

        global natural_gas_job

        natural_gas_job = scheduler.add_job(naturalGasCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='naturalgas')
        scheduler.start()
    elif selectedCommodities == 4:
        leadCommodities = LeadCommodities(socketio)
        leadCommodities.loginKite()

        global lead_job

        lead_job = scheduler.add_job(leadCommodities.startCommoditiesAlgo, trigger='cron', hour='9,10,11,12,13,14,15,16,17,18,19,20,21,22,23', minute='*',id='lead')
        scheduler.start()
    

@socketio.on('stop_script')
def stop_script(data):
    selectedCommodities = data['stopScriptFor']
    print('stop script btn clicked : ' + str(selectedCommodities))

    if selectedCommodities == 1:
        
        try:

            if gold_job is not None:
                gold_job.remove()

            # scheduler.remove_jobs('gold')

            with open('gold_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global gold_log_report
                gold_log_report = logReportObj['logReport']
                gold_log_report+= "\n" +'Script Stopped! : ' + "\n" + '---------------------------'

            logMessage = {"logReport" : gold_log_report,"selected_commodities":1}
            print(logMessage)
            socketio.emit('log_report',logMessage)

            # Now empty log report
            goldJson = {"logReport": "", "selected_commodities": 1}

            with open("gold_log_report.json", "w") as outfile:
                json.dump(goldJson, outfile)
    
        except Exception as ex:
            print(ex)

    elif selectedCommodities == 2:
        

        try:

            if silver_job is not None:
                silver_job.remove()

            # scheduler.remove_jobs('silver')

            with open('silver_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global silver_log_report
                silver_log_report = logReportObj['logReport']
                silver_log_report += "\n" +'Script Stopped! : ' + "\n" + '---------------------------'

            logMessage = {"logReport" : silver_log_report,"selected_commodities":2}
            print(logMessage)
            socketio.emit('log_report',logMessage)

            # Now empty log report
            silverJson = {"logReport": "", "selected_commodities": 2}

            with open("silver_log_report.json", "w") as outfile:
                json.dump(silverJson, outfile)

    
        except Exception as ex:
            print(ex)

    elif selectedCommodities == 3:
        try:

            if natural_gas_job is not None:
                natural_gas_job.remove()

            # scheduler.remove_jobs('naturalgas')

            with open('natural_gas_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global natural_gas_log_report
                natural_gas_log_report = logReportObj['logReport']
                natural_gas_log_report += "\n" +'Script Stopped! : ' + "\n" + '---------------------------'

            logMessage = {"logReport" : natural_gas_log_report,"selected_commodities":3}
            print(logMessage)
            socketio.emit('log_report',logMessage)

            # Now empty log report
            naturalGasJson = {"logReport": "", "selected_commodities": 3}

            with open("natural_gas_log_report.json", "w") as outfile:
                json.dump(naturalGasJson, outfile)

    
        except Exception as ex:
            print(ex)
    
    elif selectedCommodities == 4:
        try:

            if lead_job is not None:
                lead_job.remove()

            # scheduler.remove_jobs('lead')

            with open('lead_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global lead_log_report
                lead_log_report = logReportObj['logReport']
                lead_log_report += "\n" +'Script Stopped! : ' + "\n" + '---------------------------'

            logMessage = {"logReport" : lead_log_report,"selected_commodities":4}
            print(logMessage)
            socketio.emit('log_report',logMessage)

            # Now empty log report
            leadJson = {"logReport": "", "selected_commodities": 4}

            with open("lead_log_report.json", "w") as outfile:
                json.dump(leadJson, outfile)

    
        except Exception as ex:
            print(ex)
    
    
@socketio.on('save_access_token')
def save_access_token(data):
    accessToken = data['access_token']
    print('received access token : ' + accessToken)

    # write accessToken to json file
    with open("access_token.json", "w") as outfile:
        json.dump(data, outfile)

@socketio.on('browser_closed')
def browser_closed(data):
    print('browser closed : ' + str(data))
    
    # make all log report empty
    goldJson = {"logReport": "", "selected_commodities": 1}
    silverJson = {"logReport": "", "selected_commodities": 2}
    naturalGasJson = {"logReport": "", "selected_commodities": 3}
    leadJson = {"logReport": "", "selected_commodities": 4}

    with open("gold_log_report.json", "w") as outfile:
        json.dump(goldJson, outfile)

    with open("silver_log_report.json", "w") as outfile:
        json.dump(silverJson, outfile)

    with open("natural_gas_log_report.json", "w") as outfile:
        json.dump(naturalGasJson, outfile)

    with open("lead_log_report.json", "w") as outfile:
        json.dump(leadJson, outfile)


@socketio.on('commodities_change')
def commodities_change(data):
    selectedCommodities = data['selected_commodities']
    print('received selectedCommodities : ' + selectedCommodities)

    if int(selectedCommodities) == 1:
        # Now check if previous log report present or not
        try:

            with open('gold_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global gold_log_report
                gold_log_report = logReportObj['logReport']

            logMessage = {"logReport" : gold_log_report,"selected_commodities":1}
            print(logMessage)
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            print(ex)
            
    elif int(selectedCommodities) == 2:
        # Now check if previous log report present or not
        try:

            with open('silver_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global silver_log_report
                silver_log_report = logReportObj['logReport']

            logMessage = {"logReport" : silver_log_report,"selected_commodities":2}
            print(logMessage)
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            print(ex)
    elif int(selectedCommodities) == 3:
        # Now check if previous log report present or not
        try:

            with open('natural_gas_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global natural_gas_log_report
                natural_gas_log_report = logReportObj['logReport']

            logMessage = {"logReport" : natural_gas_log_report,"selected_commodities":3}
            print(logMessage)
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            print(ex)
    elif int(selectedCommodities) == 4:
        # Now check if previous log report present or not
        try:

            with open('lead_log_report.json', 'r') as openfile:
                logReportObj = json.load(openfile)

                global lead_log_report
                lead_log_report = logReportObj['logReport']

            logMessage = {"logReport" : lead_log_report,"selected_commodities":4}
            print(logMessage)
            socketio.emit('log_report',logMessage)
    
        except Exception as ex:
            print(ex)    

if __name__ == '__main__':
    socketio.run(app)