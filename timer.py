from database import *
from queue import PriorityQueue
from heapq import heappush
from copy import copy
import math


class TimingPath(object):
    def __init__(self):
        self.timing_points = []
        
        self.timing_arcs = []

class TimingSense:
    NON_UNATE = 1
    POSITIVE_UNATE = 2
    NEGATIVE_UNATE = 3

class TimingArc(object):
    def __init__(self):
        self.id = 0
        self.from_id = 0
        self.to_id = 0 
        self.timing_sense = 0
        self.fall_transition = 0
        self.rise_transition = 0
        self.fall_delay = 0
        self.rise_delay = 0
        
    def key(self):
        return (self.from_id, self.to_id)

class TimingPoint(object):
    def __init__(self):
        self.id = 0 # equals to pin id
        self.timing_arcs = []   # directional self -> other
                                # store timing_arc id

        self.incoming_arcs = []
        self.outgoing_arcs = []

        self.rise_AAT = 0
        self.rise_RAT = math.inf
        self.fall_AAT = 0
        self.fall_RAT = math.inf
        self.rise_slack = 0
        self.fall_slack = 0

        # summation of fanouts when timing_point.direction == 'output'
    
        self.load_capacitance = 0
        self.direction = 'output'
        self.topo_order = 0

    def AAT(self):
        return max(self.rise_AAT, self.fall_AAT)
    def RAT(self):
        return min(self.rise_RAT, self.fall_RAT)
    def slack(self):
        return min(self.rise_slack, self.fall_slack)


class Timer(object):
    def __init__(self):
        self.r_topo_list = []
        self.topo_list = []
        
        self.timing_points = [] # equals to pin
        self.timing_arcs = []
        
        self.topo_order = []
        self.r_topo_order = []

        self.start_points = []
        self.end_points = []

        self.arc2id = {}
        

    def timingPoint(self, pin_id):
        return self.timing_points[pin_id]

    def timingArc(self, from_id, to_id):
        return self.timing_arcs[self.key2id[(from_id, to_id)]]

    def initialize_graph(self, db, verbose = False):
        
        # For topo. sort
        num_points = len(db.circuit.pins)
        in_degree = [ 0 for _ in range(num_points) ]
        out_degree = [ 0 for _ in range(num_points) ]
        self.topo_order = [ -1 for _ in range(num_points) ]
        self.r_topo_order = [ -1 for _ in range(num_points) ]
        
        print("Create TimingPoint/Arc")
        # Initialize timing points
        for pin in db.circuit.pins:
            
            t_point = TimingPoint()    
            t_point.id = pin.id
            t_point.direction = pin.direction
 
            if pin.pin_type == PinType.PRIMARY_IN:
                self.topo_order[t_point.id] = 0
            elif pin.pin_type == PinType.PRIMARY_OUT:
                self.r_topo_order[t_point.id] = 0
            elif pin.pin_type == PinType.STANDARD_PIN:
                macro = db.liberty[db.circuit.gates[pin.gate_id].macro]
                #if macro.clocked_on == pin.port_name:
                #    self.topo_order[t_point.id] = 0
           
            self.timing_points.append(t_point)

        # Create timingArc
        for pin in db.circuit.pins:
          
            
            if pin.direction == "output":
                net = db.circuit.nets[pin.net_id]

                gate = db.circuit.gates[pin.gate_id]
                macro = db.liberty[gate.macro]

                #  ------- GATE1 --------       ------ GATE2 ------
                # | t_point1 -> t_point2 | -->  | t_point3 ...    |
                #  ----------------------       -------------------

                t_point2 = self.timing_points[net.source]

                #print("%s -> %s (source %s)" % (str(pin), net.name, str(db.get_pin(net.source))))


                # create timingArc output -> input
                for sink in net.sinks:
                    t_point3 = self.timing_points[sink]

                    sink_pin = db.circuit.pins[sink]

                    if sink_pin.pin_type == PinType.STANDARD_PIN: 
                        # accumulate load capacitance
                        sink_macro = db.liberty[db.circuit.gates[sink_pin.gate_id].macro]
                        capacitance = sink_macro[sink_pin.port_name].capacitance
                        t_point2.load_capacitance += capacitance

                    # create timing arc
                    t_arc = TimingArc()
                    t_arc.id = len(self.timing_arcs)
                    t_arc.from_id   = t_point2.id
                    t_arc.to_id     = t_point3.id
                    key = t_arc.key()
                    
                    # store
                    self.timing_arcs.append(t_arc)
                    self.arc2id[key] = t_arc.id
                    
                    t_point2.timing_arcs.append(t_arc.id)
                    in_degree[t_point3.id] += 1
                    out_degree[t_point2.id] += 1 

                    # store incoming/outgoing points
                    t_point2.outgoing_arcs.append(t_arc.id)
                    t_point3.incoming_arcs.append(t_arc.id)

                if pin.pin_type == PinType.PRIMARY_IN:
                    continue

                # create timingArc input -> output
                for (related_pin, timing) in macro[pin.port_name].timings.items():
                   
                    #print(gate.name)
                    #print(related_pin)
    
                    pin_name = "%s_%s" % (gate.name, related_pin)
                    pin_id = db.circuit.getPinId(pin_name)
                    
                    t_point1 = self.timing_points[pin_id]

                    t_arc = TimingArc()
                    t_arc.id = len(self.timing_arcs)
                    t_arc.from_id   = t_point1.id
                    t_arc.to_id     = t_point2.id

                    if timing.timing_sense == "non_unate":
                        t_arc.timing_sense = TimingSense.NON_UNATE
                    elif timing.timing_sense == "positive_unate":
                        t_arc.timing_sense = TimingSense.POSITIVE_UNATE
                    elif timing.timing_sense == "negative_unate":
                        t_arc.timing_sense = TimingSense.NEGATIVE_UNATE

                    key = t_arc.key()
                    self.timing_arcs.append(t_arc)
                    self.arc2id[key] = t_arc.id

                    t_point1.timing_arcs.append(t_arc.id)
                    in_degree[t_point2.id] += 1
                    out_degree[t_point1.id] += 1
                    
                    # store incoming/outgoing points
                    t_point1.outgoing_arcs.append(t_arc.id)
                    t_point2.incoming_arcs.append(t_arc.id)


        for (idx, t_point) in enumerate(self.timing_points):
            if in_degree[idx] == 0:
                self.start_points.append(idx)
                #print("Startpoint: %s" % str(db.get_pin(idx)))
            if out_degree[idx] == 0:
                self.end_points.append(idx)
                #print("Endpoint: %s" % str(db.get_pin(idx)))

        if verbose == True:
            for t_point in self.timing_points:
                pin = db.get_pin(t_point.id)
                print("%s %d" % (str(pin), in_degree[t_point.id]))



        print("Start Topological Sort")

        num_arcs = len(self.timing_arcs)

        # topo_sort
        Q = copy(self.start_points)
        self.topo_list = []

        while len(Q) != 0:
            t_point1 = self.timing_points[Q[0]]
            del Q[0]

            self.topo_list.append(t_point1.id)

            for arc_id in t_point1.outgoing_arcs:
                t_arc = self.timing_arcs[arc_id]

                in_degree[t_arc.to_id] -= 1

                if in_degree[t_arc.to_id] == 0:
                    Q.append(t_arc.to_id)
                    self.topo_order[t_arc.to_id] = self.topo_order[t_arc.from_id] + 1

        # r_topo_sort
        Q = copy(self.end_points)
        self.r_topo_list = []

        while len(Q) != 0:
            t_point2 = self.timing_points[Q[0]]
            del Q[0]

            self.r_topo_list.append(t_point2.id)
            
            for arc_id in t_point2.incoming_arcs:
                t_arc = self.timing_arcs[arc_id]

                out_degree[t_arc.from_id] -= 1

                if out_degree[t_arc.from_id] == 0:
                    Q.append(t_arc.from_id)
                    self.r_topo_order[t_arc.from_id] = self.r_topo_order[t_arc.to_id] + 1

        # print topo list

        if verbose == True:
            for (idx, t_point_id) in enumerate(self.topo_list):
                t_point = self.timing_points[t_point_id]
                pin = db.circuit.pins[t_point_id]
                print("%d-th %s" % (idx, pin.name))

        pass


    
    def update_timing(self, db, verbose = False):
        # forward
        for (idx, t_point_id) in enumerate(self.topo_list):
            t_point1 = self.timing_points[t_point_id]

               
            max_rise_trans = 0
            max_fall_trans = 0
            max_incr_rise_delay = 0
            max_incr_fall_delay = 0

            for in_arc_id in t_point1.incoming_arcs:
                
                in_arc = self.timing_arcs[in_arc_id]

                max_rise_trans = max(max_rise_trans, in_arc.rise_transition)
                max_fall_trans = max(max_fall_trans, in_arc.fall_transition)

                t_point0 = self.timing_points[in_arc.from_id]

                incr_rise_delay = in_arc.rise_delay + max(t_point0.fall_AAT, t_point0.rise_AAT)
                incr_fall_delay = in_arc.fall_delay + max(t_point0.fall_AAT, t_point0.rise_AAT)

                max_incr_rise_delay = max(max_incr_rise_delay, incr_rise_delay)
                max_incr_fall_delay = max(max_incr_fall_delay, incr_fall_delay)
 
            for out_arc_id in t_point1.outgoing_arcs:
                
                out_arc = self.timing_arcs[out_arc_id]

                if t_point1.direction == "input":
                    # target
                    t_point2 = self.timing_points[out_arc.to_id]
                    # timing lut
                    timing_lut = db.get_timing_lut( \
                                target_pin_id = t_point2.id,\
                                related_pin_id = t_point1.id )

                    load_cap = t_point2.load_capacitance
                    in_rise_trans = max_rise_trans
                    in_fall_trans = max_fall_trans
        
                    try:
                        if out_arc.timing_sense == TimingSense.POSITIVE_UNATE:
                            in_rise_trans = max_rise_trans
                            in_fall_trans = max_fall_trans
                        elif out_arc.timing_sense == TimingSense.NEGATIVE_UNATE:
                            in_rise_trans = max_fall_trans
                            in_fall_trans = max_rise_trans
                        elif out_arc.timing_sense == TimingSense.NON_UNATE:
                            in_rise_trans = max(max_rise_trans, max_fall_trans)
                            in_fall_trans = max(max_rise_trans, max_fall_trans)
                        else:
                            raise ValueError
                    except ValueError:
                        print("invalid timing sense")

                    # update transition time
                    out_arc.rise_transition = timing_lut.rise_transition(load_cap, in_rise_trans)
                    out_arc.fall_transition = timing_lut.fall_transition(load_cap, in_fall_trans)
                
                    # update cell delay
                    out_arc.rise_delay = timing_lut.cell_rise(load_cap, in_rise_trans)
                    out_arc.fall_delay = timing_lut.cell_fall(load_cap, in_fall_trans)
                
                else:
                    out_arc.rise_transition = max_rise_trans
                    out_arc.fall_transition = max_fall_trans

                    # interconnect delay (will be updated)
                    out_arc.rise_delay = 0
                    out_arc.fall_delay = 0

               
            if len(t_point1.incoming_arcs) == 0:
                # beginning node
                t_point1.rise_AAT = 0 + db.circuit.setup_time
                t_point1.fall_AAT = 0 + db.circuit.setup_time
            else:
                # update incr path delay
                t_point1.fall_AAT = max_incr_fall_delay
                t_point1.rise_AAT = max_incr_rise_delay


        # backward
        for (idx, t_point_id) in enumerate(self.r_topo_list):
            t_point1 = self.timing_points[t_point_id]


              
            if len(t_point1.outgoing_arcs) == 0:
                t_point1.rise_RAT = db.circuit.clock_period - db.circuit.hold_time
                t_point1.fall_RAT = db.circuit.clock_period - db.circuit.hold_time
            else:
                min_decr_rise_delay = math.inf
                min_decr_fall_delay = math.inf

                for out_arc_id in t_point1.outgoing_arcs:
                
                    out_arc = self.timing_arcs[out_arc_id]
                
                    t_point2 = self.timing_points[out_arc.to_id]

                    if t_point2.fall_RAT == math.inf or t_point2.rise_RAT == math.inf:
                        print("uninitialized value!")
                        return


                    
                    decr_rise_delay =  min(t_point2.fall_RAT, t_point2.rise_RAT) - out_arc.rise_delay
                    decr_fall_delay =  min(t_point2.fall_RAT, t_point2.rise_RAT) - out_arc.fall_delay

                    min_decr_rise_delay = min(min_decr_rise_delay, decr_rise_delay)
                    min_decr_fall_delay = min(min_decr_fall_delay, decr_fall_delay)

                t_point1.rise_RAT = min_decr_rise_delay
                t_point1.fall_RAT = min_decr_fall_delay

        WNS = math.inf
        # update slack
        for t_point in self.timing_points:
            t_point.fall_slack = t_point.fall_RAT - t_point.fall_AAT
            t_point.rise_slack = t_point.rise_RAT - t_point.rise_AAT

            WNS = min(WNS, t_point.fall_slack, t_point.rise_slack)
            
            cur_pin = db.get_pin(t_point.id)
            if verbose == True:
                print("- %s" % (cur_pin.name))
                print("\t (rise) AAT: %10f\tRAT: %10f\tSLK: %10f" % (t_point.rise_AAT, t_point.rise_RAT, t_point.rise_slack))
                print("\t (fall) AAT: %10f\tRAT: %10f\tSLK: %10f" % (t_point.fall_AAT, t_point.fall_RAT, t_point.fall_slack))

        print("WNS : %f" % WNS)


    def report_timing(self, db, nworst = 1, verbose = False):

       
        print("\n- - - - - - <report_timing> - - - - - -\n")

        slacks = [ ]

        for t_point_id in self.end_points:
            t_point = self.timing_points[t_point_id]
            slack = t_point.slack()
            slacks.append( (t_point_id, slack) )


        slacks = sorted(slacks, key=lambda elem: elem[1])

        #nworst = min(len(self.end_points), nworst)
        nworst_timing_paths = []

        for (idx, (t_point_id, slack)) in enumerate(slacks):
            #range(min(nworst, len(self.end_points))):
            #t_point_id = slacks[idx][0]

            if idx > nworst:
                break

            curr_t_point = self.timing_points[t_point_id]
            timing_path = TimingPath()
            # Start backtrace
            while True:
                timing_path.timing_points.insert(0,curr_t_point.id)
                
                # if current timing point is root, then break
                if self.topo_order[curr_t_point.id] == 0:
                    break

                worst_slack = math.inf
                prev_t_arc = 0
                prev_t_point = 0 

                for in_arc_id in curr_t_point.incoming_arcs:
                    t_arc = self.timing_arcs[in_arc_id]
                    t_point = self.timing_points[t_arc.from_id]

                    if t_point.slack() < worst_slack:
                        prev_t_arc = t_arc
                        prev_t_point = t_point
                    
                timing_path.timing_arcs.insert(0,prev_t_arc.id)
                curr_t_point = prev_t_point
            # End loop
            nworst_timing_paths.append(timing_path)

        
        for (idx, timing_path) in enumerate(nworst_timing_paths):

            start_t_point = self.timing_points[timing_path.timing_points[0]]
            end_t_point = self.timing_points[timing_path.timing_points[-1]]

            start_pin_name = db.get_pin(start_t_point.id).name
            end_pin_name = db.get_pin(end_t_point.id).name



            print("%d-th path\nStartpoint: %s\nEndpoint: %s\n" % (idx,start_pin_name, end_pin_name))
            print("-----------------------------------------------------------------------------------------------------")
            print("%-60s | %10s | %10s | %10s |" % ("Timing point", "AAT", "RAT", "Slack"))
            print("-----------------------------------------------------------------------------------------------------")
            for t_point_id in timing_path.timing_points:
                # formatting string
                cur_t_point = self.timing_points[t_point_id]
                cur_pin = db.get_pin(t_point_id)
               
                if cur_pin.pin_type == PinType.STANDARD_PIN:
                    cur_gate = db.get_gate(cur_pin.gate_id)
                    cur_macro = db.get_macro(cur_pin.id)
                    col1 = "%s/%s (%s)" % (cur_gate.name, cur_pin.port_name, cur_macro.name)
                else:
                    col1 = "%s" % (cur_pin.name)
                col2 = "%.3f" % (cur_t_point.AAT())
                col3 = "%.3f" % (cur_t_point.RAT())
                col4 = "%.3f" % (cur_t_point.slack())
                print("%-60s | %10s | %10s | %10s |" % (col1, col2, col3, col4))
                
            print("-----------------------------------------------------------------------------------------------------")
            print("\n")


            

if __name__ == '__main__':
    db = Database("contest.lib", "../bench/usb_phy/usb_phy.v") 
    #db.print()
    timer = Timer()
    timer.initialize_graph(db, verbose = False)
    timer.update_timing(db)
    timer.report_timing(db, nworst=2)







