import matplotlib.pyplot as plt
from os import walk
import csv
import numpy as np
import sys

RUBIS_NO_INSTANCE = '0'

# instance / system instance response time / node / participation time / participation rate 

class ParticipationInfo:
    def __init__(self, _instance, _start, _end, _instance_response_time, _node_list):
        self.instance = _instance
        self.start = _start
        self.end = _end
        self.instance_response_time = _instance_response_time
        self.node_list = _node_list
        self.times = []
        self.rates = []
        for _ in range(len(self.node_list)):
            self.rates.append(0.0)
            self.times.append(0.0)

        return

def get_file_list_in_dir(dir_path):
    f = []
    for (dirpath, dirnames, filenames) in walk(dir_path):
        f.extend(filenames)
        break

    return f

def get_node_name_list(dir_path):
    file_list = get_file_list_in_dir(dir_path)
    output = []
    for line in file_list:
        node_name = line.split('.')[0]
        if node_name == 'system_instance': continue
        output.append(node_name)

    return output


def write_response_time_file(dir_path, file):
    input_path = dir_path+'/'+file
    output_path = dir_path.split('/')[0] + '/response_time/' + file

    input_file = open(input_path)
    output_file = open(output_path, 'w')

    reader = csv.reader(input_file)    
    writer = csv.writer(output_file)

    for line in reader:
        if('iter' in line): # First line
            if('response_time' in line): break # Already has response time            
            line.append('response_time')
        else:
            start = float(line[2])
            end = float(line[3])
            line.append(end - start)
        writer.writerow(line)

    return

def create_response_time_file():
    dir_path = 'files/raw_data'
    file_list = get_file_list_in_dir(dir_path)
    response_time_data_list = []

    for file in file_list:
        response_time_data_list.append(write_response_time_file(dir_path, file))
    return

def get_data_from_csv(file):
    data = []
    reader = csv.reader(file)
    for line in reader: 
        data.append(line)

    return data

def get_system_instance_time_data(dir_path, start_node, end_node):
    start_node_path = dir_path+'/'+start_node+'.csv'
    end_node_path = dir_path+'/'+end_node+'.csv'

    start_node_file = open(start_node_path)
    end_node_file = open(end_node_path)

    start_node_data = get_data_from_csv(start_node_file)
    end_node_data = get_data_from_csv(end_node_file)

    _output = []

    for end_node_line in end_node_data:
        if('iter' in end_node_line):
            # end_node_data.pop(0)
            continue
        end_node_instance = end_node_line[4]
        end_node_end = end_node_line[3]

        if(end_node_instance != RUBIS_NO_INSTANCE):
            for start_node_line in start_node_data:
                if('iter' in start_node_line):
                    # start_node_data.pop(0)
                    continue

                start_node_instance = start_node_line[4]
                start_node_start = start_node_line[2]
                if(start_node_instance != end_node_instance): 
                    # start_node_data.pop(0)
                    continue
                else:
                    output_line = []
                    output_line.append(end_node_instance)
                    output_line.append(start_node_start)
                    output_line.append(end_node_end)
                    output_line.append(str(float(end_node_end) - float(start_node_start)))
                    _output.append(output_line)
    
    output = []
    output.append(['instance','start','end','response_time'])

    prev_instance = '-1'
    for line in _output:
        instance = line[0]
        if prev_instance != instance:
            output.append(line)
            prev_instance = instance
        else:
            output[-1] = line
    
    return output

def create_system_instance_time_file(start_node, end_node):
    dir_path = "files/response_time"
    # file_list = get_file_list_in_dir(dir_path)
    # node_name_list = get_node_name_list(dir_path)

    instance_time_data = get_system_instance_time_data(dir_path, start_node, end_node)
    
    output_path = dir_path+'/system_instance.csv'
    output_file = open(output_path, 'w')
    writer = csv.writer(output_file)
    writer.writerows(instance_time_data)

    return


# instance / system instance response time / node / participation time / participation rate 
def get_participation_time_data(dir_path):
    file_list = get_file_list_in_dir(dir_path)
    node_name_list = get_node_name_list(dir_path)

    # fet systek
    system_instance_file = open(dir_path+'/system_instance.csv')
    system_instance_data = get_data_from_csv(system_instance_file)

    participation_data = []

    for system_instance in system_instance_data:
        if 'start' in system_instance: continue
        instance = int(system_instance[0])
        start = float(system_instance[1])
        end = float(system_instance[2])
        response_time = float(system_instance[3])

        participation_info = ParticipationInfo(instance, start, end, response_time, node_name_list)
        participation_data.append(participation_info)

        
    for node_idx in range(len(node_name_list)):
        node_name = node_name_list[node_idx]
        file_name = file_list[node_idx]
        file_path = dir_path + '/' + file_name
        
        node_data = get_data_from_csv(open(file_path))

        if node_name == 'system_instance': continue
        
        start_idx = 1
        for participation in participation_data:
            if(start_idx >= len(node_data)): break

            for j in range(start_idx, len(node_data)):
                if(j >= len(node_data)): break
                spin_start = float(node_data[j][2])
                spin_end = float(node_data[j][3])

                if spin_start < participation.end and spin_end > participation.start:
                    _time = min(spin_end, participation.end) - max(spin_start, participation.start)
                    participation.times[node_idx] = participation.times[node_idx] + _time

    
    for participation in participation_data:        
        for i in range(len(participation.times)):
            time = participation.times[i]
            participation.rates[i] = time/participation.instance_response_time
    
    return participation_data
    
def create_participation_time_file():
    dir_path = 'files/response_time'
    participation_data = get_participation_time_data(dir_path)

    output_path = 'files/participation.csv'
    output_file = open(output_path, 'w')
    writer = csv.writer(output_file)

    writer.writerow(['instance', 'instance_respon_time', 'node', 'participation_time', 'participation_rate'])
    for participation in participation_data:
        for i in range(len(participation.node_list)):
            _instance = participation.instance
            _response_time = participation.instance_response_time
            _node = participation.node_list[i]
            _time = participation.times[i]
            _rate = participation.rates[i]
            writer.writerow([_instance, _response_time, _node, _time, _rate])
    
    return

def plot_participation_time_per_node():
    file_path = 'files/participation.csv'
    node_name_list = get_node_name_list('files/response_time')
    file = open(file_path)

    for node in node_name_list:
        if node == 'system_instance': continue
        instances = []
        response_times = []
        participation_times = []
        participation_rates = []

        reader = csv.reader(file)
        for line in reader:
            if node not in line: continue
            instances.append(int(line[0]))
            response_times.append(float(line[1]) * 1000)
            participation_times.append(float(line[3]) * 1000)
            participation_rates.append(float(line[4]) * 1000)
        file.seek(0)
            
        plt.title(node)
        plt.ylim(0.0, 500)
        plt.xlabel('instance iteration')
        plt.ylabel('participation time(ms)')
        plt.plot(instances[:-1], response_times[:-1], label='system instance')
        plt.plot(instances[:-1], participation_times[:-1], label=node)

        plt.legend()
        plt.savefig('graphs/participation_time/'+node+'.jpg')
        plt.close()
    return

def plot_participation_rate_per_node():
    file_path = 'files/participation.csv'
    node_name_list = get_node_name_list('files/response_time')
    file = open(file_path)

    for node in node_name_list:
        if node == 'system_instance': continue

        instances = []
        response_times = []
        participation_times = []
        participation_rates = []

        reader = csv.reader(file)
        for line in reader:
            if node not in line: continue
            instances.append(int(line[0]))
            response_times.append(float(line[1]))
            participation_times.append(float(line[3]))
            participation_rates.append(float(line[4]))
        file.seek(0)
            
        plt.title(node)

        plt.plot(instances[:-1], participation_rates[:-1])
        plt.ylim(0.0, 1.0)
        plt.xlabel('instance iteration')
        plt.ylabel('participation rate')
        plt.legend()
        plt.savefig('graphs/participation_rate/'+node+'.jpg')
        plt.close()

def plot_avg_participation():
    file_path = 'files/participation.csv'
    node_name_list = get_node_name_list('files/response_time')
    file = open(file_path)

    avg_time_list = []
    avg_rate_list = []

    # each node
    for node in node_name_list:
        if node == 'system_instance': continue 

        instances = []
        response_times = []
        participation_times = []
        participation_rates = []

        reader = csv.reader(file)
        for line in reader:
            if node not in line: continue
            instances.append(int(line[0]))
            response_times.append(float(line[1]))
            participation_times.append(float(line[3]) * 1000)
            participation_rates.append(float(line[4]))
        file.seek(0)
        
        avg_time_list.append(sum(participation_times)/len(participation_times))
        avg_rate_list.append(sum(participation_rates)/len(participation_rates))
    
    # Get start instance number
    next(reader)
    start_instance = int(next(reader)[0])
    
    file_path = 'files/response_time/system_instance.csv'
    file = open(file_path)
    
    # system instasnce
    reader = csv.reader(file)
    system_instance_avg_times = []
    for line in reader:
        if 'instance' in line: continue
        if int(line[0]) < start_instance: continue
        system_instance_avg_times.append(float(line[3]) * 1000)
        
    node_name_list.append('system_instance')
    avg_time_list.append(sum(system_instance_avg_times)/len(system_instance_avg_times))
    avg_rate_list.append(1.0)
    
    order = np.argsort(avg_time_list)
    
    node_name_list = [node_name_list[i] for i in order]
    
    avg_time_list = [avg_time_list[i] for i in order]
    avg_rate_list = [avg_rate_list[i] for i in order]
    
    plt.figure(figsize=(19,8))
    plt.barh(node_name_list, avg_time_list)
    plt.xlim(0.0, 400.0)
    plt.xlabel('Participatio Time(ms)')
    plt.ylabel('Node name')
    plt.title('Average Participation Time')
    plt.savefig('graphs/participation_time.png')
    
    plt.close
    
    plt.figure(figsize=(19,8))
    plt.barh(node_name_list, avg_rate_list)
    plt.xlabel('Participatio Rate')
    plt.ylabel('Node name')
    plt.title('Average Participation Rate')
    plt.savefig('graphs/participation_rate.png')
    
    plt.close
    
    
    
    return


def main():
    # input: Bane of start and end node
    start_node = 'voxel_grid_filter'
    end_node = 'twist_gate'

    ## Get response time from raw data file
    create_response_time_file() 

    ## Get response time of system instance
    create_system_instance_time_file(start_node, end_node)
    
    # Get participation information of system instance
    create_participation_time_file()

    # Plot
    plot_participation_time_per_node()
    plot_participation_rate_per_node()
    plot_avg_participation()

    # <Profiling>
    # [1]   system instance -> # / start / end / response time
    # [2]   participation time(per node) -> spin which 1) start before instance end & 2) end after instance_start
    #       max(start, instance start) // min(end, instance end)
    # [3]   participation rate -> almost same with [2]
    # [4]   instance overlap -> find duration of tartet instance which start before prev instances are done




    return

if __name__ == '__main__':
    main()