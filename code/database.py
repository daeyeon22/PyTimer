import liberty.parser 
from verilog_parser import *
from scipy import interpolate

import numpy as np

class Database(object):
    def __init__(self, lib_path, verilog_path):
        self.liberty = self.parse_liberty(lib_path)
        self.circuit = self.parse_verilog(verilog_path)

    def get_net(self, net_id):
        return self.circuit.nets[net_id]

    def get_gate(self, gate_id):
        return self.circuit.gates[gate_id]

    def get_pin(self, pin_id):
        return self.circuit.pins[pin_id]

    def get_macro(self, pin_id):
        return self.liberty[self.circuit.gates[self.circuit.pins[pin_id].gate_id].macro]

    def get_macro_pin(self, pin_id):
        return self.get_macro(pin_id)[self.circuit.pins[pin_id].port_name]

    def get_port_name(self, pin_id):
        return self.circuit.pins[pin_id].port_name

    def get_timing_lut(self, target_pin_id, related_pin_id):
        timing =  self.get_macro_pin(target_pin_id)[self.get_port_name(related_pin_id)]
        return timing


    def print(self):
        
        for gate in self.circuit.gates:
            print("- %s (%s)" % (gate.name, gate.macro))
            for in_pin_id in gate.input_pins:
                print("     <IN > %s" % str(self.get_pin(in_pin_id)))

            for out_pin_id in gate.output_pins:
                out_pin = self.get_pin(out_pin_id)
                out_net = self.get_net(out_pin.net_id)
                print("     <OUT> %s -> (net: %s)"  % (str(out_pin), out_net.name))
            print("\n")

        for net in self.circuit.nets:
            source_pin = self.get_pin(net.source)

            print("- %s (source : %s)" % (net.name, source_pin.name))

            for sink_pin_id in net.sinks:
                sink_pin = self.get_pin(sink_pin_id)
                print("     <sink> %s" % str(sink_pin))

            print("\n")













    def getInCap(self, pin_id):
        pin = self.circuit.pin(pin_id)
        
        if pin.direction == 'output':
            print("only available when direction of pin is 'input'!")
            return 0

        if pin.type != PinType.STANDARD_Pin:
            return 0

        gate = self.circuit.gate(pin.gate_id)
        macro_pin = self.liberty[gate.macro][pin.port_name]
        return macro_pin.capacitance





    def parse_liberty(self,libPath):
        my_liberty = Liberty()

        lib = liberty.parser.parse_liberty(open(libPath).read())

    
    
    
        for lib_cell in lib.get_groups('cell'):
            macro = Macro()
            macro.name = str(lib_cell.args[0]).strip('"')
            for (attr, val) in lib_cell.attributes.items():
                setattr(macro, attr, val)
                #print(attr, val)

            for lib_ff in lib_cell.get_groups('ff'):
                for (attr, val) in lib_ff.attributes.items():
                    setattr(macro, attr, val)

            for lib_macro_pin in lib_cell.get_groups('pin'):
                macro_pin = MacroPin()
                macro_pin.name = str(lib_macro_pin.args[0]).strip('"')

                for (attr, val) in lib_macro_pin.attributes.items():
                    setattr(macro_pin, attr, val)
                    #print(attr, val)


                for lib_macro_pin_timing in lib_macro_pin.get_groups('timing'):
                    timing_attr_list = [ 'cell_rise', 'rise_transition', 'cell_fall', 'fall_transition' ]
                    #print("###")
                    timing = Timing()
                    for (attr, val) in lib_macro_pin_timing.attributes.items():
                        setattr(timing, attr, str(val).strip('"'))
                        #print(attr, str(val).strip('"'))
                    
                    for timing_attr in timing_attr_list:
                        for lib_timing_lut in lib_macro_pin_timing.get_groups(timing_attr):
                            #timing.index_1[timing_attr] = lib_timing_lut.get_array('index_1')
                            #timing.index_2[timing_attr] = lib_timing_lut.get_array('index_2')
                            #timing.values[timing_attr] = lib_timing_lut.get_array('values')
                   

                            index_1 = [float(val) for val in lib_timing_lut.get_array('index_1')[0]]
                            index_2 = [float(val) for val in lib_timing_lut.get_array('index_2')[0]]
                            values = np.transpose([[float(val) for val in arr] for arr in lib_timing_lut.get_array('values')])
                            timing.luts[timing_attr] = interpolate.interp2d(index_1, index_2, values)


                    macro_pin.timings[timing.related_pin] = timing
                
                macro.pins[macro_pin.name] = macro_pin

            my_liberty.macros[macro.name] = macro


        return my_liberty

    def parse_verilog(self,verilog_path):
        my_circuit = Circuit()
        
        netlist = parse_verilog(open(verilog_path).read())

        module = netlist.modules[0]

        my_circuit.module_name = module.module_name
        
        for net in module.net_declarations:
            my_net = Net()
            my_net.id = len(my_circuit.nets)
            my_net.name = net.net_name
            my_circuit.net2id[my_net.name] = my_net.id
            my_circuit.nets.append(my_net)

        for pi in module.input_declarations:
            my_prim_in = Pin()
            my_prim_in.id = len(my_circuit.pins)
            my_prim_in.pin_type = PinType.PRIMARY_IN
            my_prim_in.name = pi.net_name
       
            #print("pi.net_name : %s" %  pi.net_name)

            if not pi.net_name in my_circuit.net2id:
                #print("does not exist")
                my_net = Net()
                my_net.id = len(my_circuit.nets)
                my_net.name = pi.net_name
                my_circuit.net2id[pi.net_name] = my_net.id
                my_circuit.nets.append(my_net)
           


            my_prim_in.net_id = my_circuit.net2id[pi.net_name]
            my_prim_in.direction = "output"

            #
            my_net = my_circuit.nets[my_prim_in.net_id]
            my_net.source = my_prim_in.id
            my_net.terminals.insert(0, my_prim_in.id)
            
            my_circuit.pin2id[my_prim_in.name] = my_prim_in.id
            my_circuit.pins.append(my_prim_in)
            my_circuit.primary_inputs.append(my_prim_in.id)

        for po in module.output_declarations:
            my_prim_out = Pin()
            my_prim_out.id = len(my_circuit.pins)
            my_prim_out.pin_type = PinType.PRIMARY_OUT
            my_prim_out.name = po.net_name

            if not po.net_name in my_circuit.net2id:
                my_net = Net()
                my_net.id = len(my_circuit.nets)
                my_net.name = po.net_name
                my_circuit.net2id[po.net_name] = my_net.id
                my_circuit.nets.append(my_net)
            
            my_prim_out.net_id = my_circuit.net2id[po.net_name]
            my_prim_out.direction = "input"
            
            my_net = my_circuit.nets[my_prim_out.net_id]
            my_net.sinks.append(my_prim_out.id)
            my_net.terminals.append(my_prim_out.id)

    
            my_circuit.pin2id[my_prim_out.name] = my_prim_out.id
            my_circuit.pins.append(my_prim_out)
            my_circuit.primary_outputs.append(my_prim_out.id)


        for inst in module.module_instances:
            my_gate = Gate()
            my_gate.id = len(my_circuit.gates)
            my_gate.macro = inst.module_name
            my_gate.name = inst.instance_name

            my_circuit.gate2id[my_gate.name] = my_gate.id
            my_circuit.gates.append(my_gate)
            #print(my_gate.macro, type(my_gate.macro))
            my_macro = self.liberty[my_gate.macro]

            for (port_name, net_name) in inst.ports.items():
                my_pin = Pin()
                my_pin.id = len(my_circuit.pins)
                my_pin.pin_type = PinType.STANDARD_PIN
                my_pin.name = "%s_%s" % (my_gate.name, port_name)
                my_pin.port_name = port_name
                my_pin.gate_id = my_gate.id
                my_pin.net_id = my_circuit.net2id[net_name]

                my_macro_pin = my_macro[port_name]
                my_net = my_circuit.net(net_name)
                my_pin.direction = my_macro_pin.direction
                if my_pin.direction == "input":
                    my_gate.input_pins.append(my_pin.id)
                    #
                    my_net.sinks.append(my_pin.id)
                    my_net.terminals.append(my_pin.id)
                elif my_pin.direction == "output":
                    my_gate.output_pins.append(my_pin.id)
                    #
                    my_net.source = my_pin.id
                    my_net.terminals.insert(0, my_pin.id)
                elif my_pin.direction == "inout":
                    print("?????")

                my_circuit.pin2id[my_pin.name] = my_pin.id
                my_circuit.pins.append(my_pin)
                
        return my_circuit
         


class Circuit(object):
    def __init__(self):
        self.module_name = ""
        self.primary_inputs = []
        self.primary_outputs = []
        self.gates = []
        self.pins = []
        self.nets = []

        # hash map 
        self.net2id = {}
        self.pin2id = {}
        self.gate2id = {}


        self.clock_period = 300 #
        self.hold_time = 0
        self.setup_time = 0



    # getter
    def net(self, net_name):
        return self.nets[self.net2id[net_name]]
    def pin(self, pin_name):
        return self.pins[self.pin2id[pin_name]]
    def gate(self, gate_name):
        return self.gates[self.gate2id[gate_name]]
    def getNetId(self, net_name):
        return self.net2id[net_name]
    def getGateId(self, gate_name):
        return self.gate2id[gate_name]
    def getPinId(self, pin_name):
        return self.pin2id[pin_name]




class Gate(object):
    def __init__(self):
        self.id = 0
        self.name = ""
        self.macro = 0 #macroid #Macro()
        self.input_pins = []    # store pin ids
        self.output_pins = []   
        self.fanins = []        # store pin ids
        self.fanouts = []

class PinType:
    PRIMARY_IN = 1
    PRIMARY_OUT = 2
    STANDARD_PIN = 3
    

class Pin(object):
    def __init__(self):
        self.id = 0
        self.pin_type = PinType.STANDARD_PIN

        self.net_id = 0 # net id
        self.name = ""
        self.port_name = ""
        self.gate_id = 0 # gate id
        self.direction = ""

        # Updated by Timer
        self.capacitance = 0
        self.total_capacitance = 0
        self.rise_transition = 0
        self.fall_transition = 0
        self.rise_slack = 0
        self.fall_slack = 0
        self.rise_AAT = 0
        self.fall_AAT = 0
        self.rise_delay = 0
        self.fall_delay = 0

    def __str__(self):
        return "%s %s" % (self.name, self.direction)



class Net(object):
    def __init__(self):
        self.id = 0
        self.name = ""
        self.source = 0
        self.sinks = []
        self.terminals = [] # source id is always at the beginning of list


class Liberty(object):
    def __init__(self):
        self.macros = {}
        self.time_unit = ""
        self.current_unit = ""
        self.voltage_unit = ""
        self.leakage_power_unit = ""
        self.capacitive_load_unit = ""


    def __getitem__(self, macro_name):
        return self.macros[macro_name]

    def getMacro(self, macro_name):
        return self.macros[macro_name]    

class Macro(object):
    def __init__(self):
        self.name = ""
        self.area = 0
        self.cell_leak_power = 0
        self.pins = {}

        # If clocked
        self.clocked_on = ""
        self.next_state = ""

    def __getitem__(self, pin_name):
        return self.pins[pin_name]

    

class MacroPin(object):
    def __init__(self):
        self.name = ""
        self.direction = ""
        self.function = ""
        self.max_capacitance = 0
        self.capacitance = 0
        self.max_transition = 0
        self.rise_capacitance = 0
        self.fall_capacitance = 0
        self.timings = {}

    def __getitem__(self, related_pin):
        return self.timings[related_pin]

    

class Timing(object):
    def __init__(self):
        self.related_pin = ""
        self.timing_sense = ""
        self.luts = {}

        #self.index_1 = {}
        #self.index_2 = {}
        #self.values = {}
    
    def rise_transition(self, load_cap, in_trans):
        return self.luts['rise_transition'](load_cap, in_trans)[0]
    def fall_transition(self, load_cap, in_trans):
        return self.luts['fall_transition'](load_cap, in_trans)[0]
    def cell_rise(self, load_cap, in_trans):
        return self.luts['cell_rise'](load_cap, in_trans)[0]
    def cell_fall(self, load_cap, in_trans):
        return self.luts['cell_fall'](load_cap, in_trans)[0]

   
        
if __name__ == '__main__':
    print("hi")


        





