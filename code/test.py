
from liberty.parser import parse_liberty, test_parse_liberty_freepdk

#test_parse_liberty_freepdk()



library = parse_liberty(open("asap7.lib").read())
outFile = open("ASAP7.txt",'w')
cells = library.get_groups('cell')

for cell in cells:
    outFile.write("%s %s\n" % ( cell.group_name, cell.args[0] ))
    for (attr, val) in cell.attributes.items():
        outFile.write("\t%s %s\n" % (attr, val))
    
    pins = cell.get_groups('pin')
    for pin in pins:
        outFile.write("\t%s %s\n" % ( pin.group_name, pin.args[0] ))
        for (attr, val) in pin.attributes.items():
            if isinstance(val, list):
                outFile.write("\t\t%s %s\n" % (attr, ' '.join([str(i) for i in val])))
            else:
                outFile.write("\t\t%s %s\n" % (attr, val))


        timings = pin.get_groups('timing')

        for timing in timings:
            outFile.write("\t\t%s\n" % (timing.group_name))
            for (attr, val) in timing.attributes.items():
                if isinstance(val, list):
                    outFile.write("\t\t\t%s %s\n" % (attr, ' '.join([str(i) for i in val])))
                else:
                    outFile.write("\t\t\t%s %s\n" % (attr, val))




            attr_list = [ 'cell_rise', 'rise_transition', 'cell_fall', 'fall_transition' ]

            for attr in attr_list:
                for timing_lut in timing.get_groups(attr):
                    outFile.write("\t\t\t%s %s\n" % ( timing_lut.group_name, timing_lut.args[0] ))
                    index_1 = timing_lut.get_array('index_1')
                    index_2 = timing_lut.get_array('index_2')
                    values = timing_lut.get_array('values')
                    outFile.write("\t\t\t\tindex_1 %s\n" % (' '.join([str(i) for i in index_1[0]])))
                    outFile.write("\t\t\t\tindex_2 %s\n" % (' '.join([str(i) for i in index_2[0]])))
                    
                    outFile.write("\t\t\t\tvalues\n")
                    for val_arr in values:
                        outFile.write("\t\t\t\t\t%s\n" % (' '.join([str(i) for i in val_arr])))
                    outFile.write("\t\t\t\tend\n") # end values
                    
                    outFile.write("\t\t\tend\n") # end timing lut
            outFile.write("\t\tend\n") # end timing
        
        outFile.write("\tend\n") # end pin

    outFile.write("end\n") # end cell
outFile.close()






#print(str(library))


