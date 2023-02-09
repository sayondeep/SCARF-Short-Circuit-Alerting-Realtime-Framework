import cmd
import json
import paho.mqtt.client as MqttClient
import random
import threading
import time


class Appliance(cmd.Cmd):
    def __init__(self, args):
        super().__init__()
        self.Device = args['Device']
        self.prompt = 'Home > Appliance({Device}) > '.format(Device=self.Device)
        self.Brand = args['Brand']

        self.Min_Watt = args['Min_Watt']
        self.Max_Watt = args['Max_Watt']

        self.Voltage=0
        self.Current=0
        self.Watt=0


        self.mqtt_client = MqttClient.Client(self.Device)
        #self.mqtt_client.username_pw_set('admin', 'hivemq')
        self.mqtt_client.username_pw_set('guest', 'guest')
        #self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.connect('127.0.0.1', 1883)
        self.mqtt_client.loop_start()
        self.thread = threading.Thread(target=self.start_client)
        self.running = True
        self.thread.start()

    def start_client(self):
        while (self.running):
            self.Voltage = 240 + random.uniform(-1 * 0.3 * 240, 0.2 * 240)
            self.Watt = random.uniform(self.Min_Watt, self.Max_Watt)
            self.Current = (self.Watt / self.Voltage)
            self.mqtt_client.publish('{Device}'.format(Device=self.Device),
                                     '''appliance,appliance={Device} V={Voltage},I={Current},W={Watt}'''.format(
                                     Voltage=self.Voltage,Current=self.Current,Watt=self.Watt,Device=self.Device,))
            time.sleep(5)

    def stop_client(self):
        print('Stopping Appliance{Device}...'.format(Device=self.Device))
        self.running = False
        self.thread.join(1)

    def do_list(self, line):
        """Show List of available parameters"""
        print("1. Min_Watt")
        print("2. Max_Watt")

    def do_set(self, line):
        """Set Substation Simulation Parameters (set parameter_name value)"""
        args = line.split()
        if (hasattr(self, args[0])):
            setattr(self, args[0], float(args[1]))
        else:
            print("Error: Invalid Parameter")

    def do_exit(self, line):
        """Go back to previous menu"""
        return True


class Home(cmd.Cmd):
    """PowerGrid Simulator Console"""
    prompt = 'Home > '

    def __init__(self):
        super().__init__()
        with open('homestructure.json') as homestructureFile:
            self.homestructure = json.load(homestructureFile)
            self.Appliances = {}
            for app in self.homestructure['Appliances']:
                appliance = Appliance(app)
                self.Appliances[app['Device']] = appliance

    def do_show(self, line):
        """Show list of substations"""
        for appliance in self.Appliances:
            print(appliance)

    def do_use(self, Device):
        """Select Substation"""
        if Device in self.Appliances:
            self.Appliances[Device].cmdloop()
        else:
            print("Error: Unknown Device ")

    def do_exit(self, line):
        """Shutdown PowerGrid Simulator"""
        for Appliance in self.Appliances:
            self.Appliances[Appliance].stop_client()
        return True

    def do_EOF(self, line):
        """Shutdown PowerGrid Simulator"""
        for Appliance in self.Appliances:
            self.Appliances[Appliance].stop_client()
        return True


if __name__ == '__main__':
    Home().cmdloop()
