from liberty.parser import parse_liberty
from verilog_parser import *


def parseLiberty(libPath):

    my_liberty = Liberty()

    lib = parse_liberty(open(libPath).read())
    for lib_cell in lib.get_groups('cell'):
        macro = Macro()
        macro.name = lib_cell.args[0]
        for (attr, val) in lib_cell.attributes.items():
            setattr(macro, attr, val)
            print(attr, val)

        for lib_macro_pin in lib_cell.get_groups('pin'):
            macro_pin = MacroPin()
            macro_pin.name = lib_macro_pin.args[0]

            for (attr, val) in lib_macro_pin.attributes.items():
                setattr(macro_pin, attr, val)
                print(attr, val)

            for lib_macro_pin_timing in lib_macro_pin.get_groups('timing'):
                attr_list = [ 'cell_rise', 'rise_transition', 'cell_fall', 'fall_transition' ]

                for attr in attr_list:
                    for lib_timing_lut in lib_macro_pin_timing.get_groups(attr):
                        timing_lut = Timing()
                        setattr(timing_lut, 'timing_attr', attr)
                        setattr(timing_lut, 'index_1', lib_timing_lut.get_array('index_1'))
                        setattr(timing_lut, 'index_2', lib_timing_lut.get_array('index_2'))
                        setattr(timing_lut, 'values', lib_timing_lut.get_array('values'))

                        macro_pin.timings[attr] = timing_lut

            macro.pins[macro_pin.name] = macro_pin

        my_liberty.macros[macro.name] = macro

    return my_liberty

def parseVerilog(verilog_path):
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
        my_prim_in.net_id = my_circuit.net2id[pi.net_name]
        my_prim_in.direction = "output"
        my_circuit.pin2id[my_prim_in.name] = my_prim_in.id
        my_circuit.pins.append(my_prim_in)
        my_circuit.primary_inputs.append(my_prim_in.id)

    for po in module.output_declarations:
        my_prim_out = Pin()
        my_prim_out.id = len(my_circuit.pins)
        my_prim_out.pin_type = PinType.PRIMARY_OUT
        my_prim_out.name = po.net_name
        my_prim_out.net_id = my_circuit.net2id[po.net_name]
        my_prim_out.direction = "input"
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
        
        
if __name__ == '__main__':
    parseLiberty('asap7.lib')



        





