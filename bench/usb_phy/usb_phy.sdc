# Synopsys Design Constraints Format
# Copyright © 2011, Synopsys, Inc. and others. All Rights reserved.

# clock definition
set_units -time ps -resistance kOhm -capacitance fF -voltage V -current mA
create_clock -name clk -period 300.0 [get_ports clk]

# input delays
set_input_delay 0.0 [get_ports DataOut_i_0_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_1_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_2_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_3_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_4_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_5_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_6_] -clock clk
set_input_delay 0.0 [get_ports DataOut_i_7_] -clock clk
set_input_delay 0.0 [get_ports TxValid_i] -clock clk
set_input_delay 0.0 [get_ports phy_tx_mode] -clock clk
set_input_delay 0.0 [get_ports rst] -clock clk
set_input_delay 0.0 [get_ports rxd] -clock clk
set_input_delay 0.0 [get_ports rxdn] -clock clk
set_input_delay 0.0 [get_ports rxdp] -clock clk

# input drivers
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_0_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_1_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_2_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_3_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_4_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_5_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_6_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports DataOut_i_7_] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports TxValid_i] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports phy_tx_mode] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports rst] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports rxd] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports rxdn] -input_transition_fall 80.0 -input_transition_rise 80.0
set_driving_cell -lib_cell in01f80 -pin o [get_ports rxdp] -input_transition_fall 80.0 -input_transition_rise 80.0

# output delays
set_output_delay 0.0 [get_ports DataIn_o_0_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_1_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_2_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_3_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_4_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_5_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_6_] -clock clk
set_output_delay 0.0 [get_ports DataIn_o_7_] -clock clk
set_output_delay 0.0 [get_ports LineState_o_0_] -clock clk
set_output_delay 0.0 [get_ports LineState_o_1_] -clock clk
set_output_delay 0.0 [get_ports RxActive_o] -clock clk
set_output_delay 0.0 [get_ports RxError_o] -clock clk
set_output_delay 0.0 [get_ports RxValid_o] -clock clk
set_output_delay 0.0 [get_ports TxReady_o] -clock clk
set_output_delay 0.0 [get_ports g1897_u0_o] -clock clk
set_output_delay 0.0 [get_ports txdn] -clock clk
set_output_delay 0.0 [get_ports txdp] -clock clk
set_output_delay 0.0 [get_ports txoe] -clock clk
set_output_delay 0.0 [get_ports usb_rst] -clock clk

# output loads
set_load -pin_load 4.0 [get_ports DataIn_o_0_]
set_load -pin_load 4.0 [get_ports DataIn_o_1_]
set_load -pin_load 4.0 [get_ports DataIn_o_2_]
set_load -pin_load 4.0 [get_ports DataIn_o_3_]
set_load -pin_load 4.0 [get_ports DataIn_o_4_]
set_load -pin_load 4.0 [get_ports DataIn_o_5_]
set_load -pin_load 4.0 [get_ports DataIn_o_6_]
set_load -pin_load 4.0 [get_ports DataIn_o_7_]
set_load -pin_load 4.0 [get_ports LineState_o_0_]
set_load -pin_load 4.0 [get_ports LineState_o_1_]
set_load -pin_load 4.0 [get_ports RxActive_o]
set_load -pin_load 4.0 [get_ports RxError_o]
set_load -pin_load 4.0 [get_ports RxValid_o]
set_load -pin_load 4.0 [get_ports TxReady_o]
set_load -pin_load 4.0 [get_ports g1897_u0_o]
set_load -pin_load 4.0 [get_ports txdn]
set_load -pin_load 4.0 [get_ports txdp]
set_load -pin_load 4.0 [get_ports txoe]
set_load -pin_load 4.0 [get_ports usb_rst]
