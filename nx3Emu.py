import sys,os,logging,netifaces
from PyQt5.QtWidgets import QApplication, QDialog,QMainWindow
from ui_mainWindow import Ui_CeresEmulatorWindow
import paho.mqtt.client as mqtt
import json
import datetime
class NX3Emu():
    """ System Variables: """
    log = False
    app = False
    ui = False
    window = False
    connected = False
    mqtt_in = False
    mqtt_out = False
    host = False
    user = False
    port = 1883
    pw = False
    device_id = False
    device_type = False
    device_uuid = False
    dev_auth = False
    """ EMULATOR Variables: """
    """ Time """
    time = 0
    """ Sync Input and Output Power: """
    sync_io_po = False
    """ Power factor: """
    pf = 0.90
    
    

    """ Each topic needs its own specific handler: """
    def topic_handle_time(self,msg):
        self.time = datetime.datetime.strptime(msg.payload.decode(),"%y/%m/%d %H:%M:%S")
        self.ui.connect_dateTime.setDateTime(self.time)
        """ If device isn't authenticated... ask for a token: """
        if (self.dev_auth is False):
            ipaddr = netifaces.ifaddresses(netifaces.interfaces()[1])[2][0]['addr']
            atkn = json.dumps({"request":{"id":str(self.device_id),"uuid":str(self.device_uuid),"type":str(self.device_type),"ipaddr":ipaddr}})
            self.mqtt_in.publish("device.requests.auth",atkn);

        
    """ Route and Handle incoming Messages: """
    def on_message(self,client,userdata,msg):
        self.log.info("Topic: %s",msg.topic)
        if (msg.topic == "time"): self.topic_handle_time(msg)

    """ Handle Connection Behaviour: """
    def on_connect(self,client, userdata, flags, rc):
        self.ui.connect_status.setText("CONNECTED - Requesting AUTH")
        self.log.info("Connected. Awaiting Auth..")
        """ Subscribe to the time, and auth channels: """
        self.mqtt_in.subscribe('time')
        self.mqtt_in.subscribe("device.requests.auth_"+self.device_id)
        """ Now request an auth token from the server: """
        
        
    """ Function to Connect to the Server: """
    def go_connect(self):
        self.host = self.ui.connect_host.text()
        self.port = self.ui.connect_port.value()
        self.user = self.ui.connect_user.text()
        self.pw = self.ui.connect_pw.text()
        self.device_type = self.ui.connect_device_type.text()
        self.device_id = self.ui.connect_device_id.text()
        self.device_uuid = self.ui.connect_device_uuid.text()
        if (self.host == ""):
            self.log.error("mqtt_in host required.")
            self.window.statusBar().showMessage("Specify an mqtt_in host in the Connection tab.",5000)
            self.ui.connect_host.setFocus()
            return;
        if (self.device_type == ""):
            self.log.error("CERES Device Type  required.")
            self.window.statusBar().showMessage("Specify a Device Type  in the Connection tab.",5000)
            self.ui.connect_device_type.setFocus()
            return;
        if (self.device_id == ""):
            self.log.error("CERES Device ID  required.")
            self.window.statusBar().showMessage("Specify a Device ID  in the Connection tab.",5000)
            self.ui.connect_device_id.setFocus()
            return;
        if (self.device_uuid == ""):
            self.log.error("CERES Device UUID required.")
            self.window.statusBar().showMessage("Specify a Device Type  in the Connection tab.",5000)
            self.ui.connect_device_uuid.setFocus()
            return;

        new_port = self.ui.connect_port.value();
        if (new_port == 0):
            self.log.info("Default port of 1883 selected.")
            self.ui.connect_port.setValue(1883);
        else:
            new_port = self.ui.connect_port.value();
            self.log.info("Port %s specified.",new_port)    
            self.port = new_port

        self.window.statusBar().showMessage("Connecting to mqtt_in....",5000)
        self.mqtt_in = mqtt.Client()
        self.mqtt_out = mqtt.Client()
        self.mqtt_in.on_connect = self.on_connect
        self.mqtt_in.on_message = self.on_message
        
        self.ui.connect_status.setText("CONNECTING...")

        if (self.user != "") and (self.pw != ""):
            self.mqtt_in.username_pw_set(self.user,self.pw)
            self.log.info("Connection username set to %s.",self.user)
        self.log.info("Intiating connection to mqtt_in: tcp://%s:%s...",self.host,self.port)
        self.mqtt_in.connect_async(self.host,self.port)
        self.mqtt_in.loop_start()
        self.mqtt_out.connect(self.host,self.port)
        return True
    """ Handle sync_io_po changes: """
    def sync_iopoHandle(self):
        self.log.info("Changing Input/Output PO Sync")
        
    """ Calculate and set PF from Slider: """
    def updatePf(self):
        self.pf = self.ui.input_pf.value()/100
        self.ui.input_pf_view.setText(str(self.pf))
        
    """ Handle Connection Triggers """
    def goConnect(self):
        if (self.connected is False):
            self.log.info("Starting Connection...")
            ret = self.go_connect()
            if (ret is True):
                self.ui.connect.setDisabled(True)
                self.ui.disconnect.setDisabled(False)
                self.connected = True
        else:
            self.log.info("Closing Connection...")
            self.ui.connect.setDisabled(False)
            self.ui.disconnect.setDisabled(True)
            self.connected = False
            
        
        
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.log = logging.getLogger('[NX3:Emulator]')
        self.log.info('Starting: Loading UI...')
        self.app = QApplication(sys.argv)
        self.window = QMainWindow()
        self.ui = Ui_CeresEmulatorWindow()
        self.ui.setupUi(self.window)
        """ Signals gotta get connected: """
        self.log.info('Starting: Connecting Signals...')
        self.ui.connect.clicked.connect(self.goConnect)
        self.ui.disconnect.clicked.connect(self.goConnect)
        self.ui.input_pf.valueChanged.connect(self.updatePf)
        
        """ now connect the buttons: """
        self.log.info('Starting: Init buttons...')
        self.ui.connect.setDisabled(False)
        self.ui.disconnect.setDisabled(True)
        
    def start(self):
        self.window.show()
        self.window.statusBar().showMessage("Welcome to the NX3 Emulator!",5000)
        sys.exit(self.app.exec_())
