#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import pandapower as pp
import numpy as np
from gamspy import Container, Set, Alias, Parameter

def extract_info(filepath):
    #Load network in pandapower from .xlsx file
    net = pp.from_excel(filepath)
    
    #find the zero-injection buses of network, as the buses where no loads, static generator, shunt elements, etc. are connected 
    zero_injection_buses = np.array(
    [
        bus
        for bus in net.bus.index
        if all(
            not net[element].in_service[net[element].bus == bus].any() for element in ["load", "sgen", "gen", "ext_grid", "ward", "xward", "storage"]
        )
    ]
)
    #create a set with all buses of the network and one with the zero-injection ones
    net_bus_set = set(net.bus.index)
    zero_injection_bus_set = set(zero_injection_buses)

    #find the buses of the network with injection as the difference between the previous sets
    injection_buses = net_bus_set - zero_injection_bus_set

    #convert the set into an array
    injection_buses = np.array(list(injection_buses))
    
    #find the buses that are out of service
    out_of_service_buses=net.bus.index[net.bus['in_service'] == False]

    #run a power flow in this network
    pp.runpp(net)

    #Stage 1: Handling of switches and buses reduction
    
    #The following piece of code deals with the duplicate nodes, due to the existence of switches. By the end of this code, two arrays are created, 
    #one with the original buses to consider, and another with the duplicates 
    columns_to_isolate = ["bus", "element", "et", "closed"]
    isolated_data = net.switch[columns_to_isolate].copy()

    #We only care about closed switches between buses, this is stated through the following command. If the switches are not closed, the buses are not equivalent.
    filtered_data = isolated_data[(isolated_data['et'] == 'b') & (isolated_data['closed'] == True)].copy()
    columns_to_isolate = ["bus", "element"]

    #We isolate the "bus" and "element" columns and create a hashmap, that maps an original bus with its duplicate.
    switch_hashmap = filtered_data[columns_to_isolate].copy()

    #This code here accounts for the possibility that the original bus is out of service. If it is out of service, but the duplicate is not, then the duplicate     is set as the original bus.
    for index, row in switch_hashmap.iterrows():
        if row['bus'] in out_of_service_buses:
            # Step 1a: If the bus is found, check if the corresponding element is also in out_of_service_buses
            if row['element'] not in out_of_service_buses:
                # Step 1aa: Swap the entries of bus and element columns
                temp = row['bus']
                switch_hashmap.at[index, 'bus'] = row['element']
                switch_hashmap.at[index, 'element'] = temp

    #After having finalised the switch_hashmap, we get the column with the original buses (buses_to_keep) and the one with the duplicates (buses_to_remove)
    buses_to_remove = switch_hashmap.iloc[:, 1].tolist()
    buses_to_keep=switch_hashmap.iloc[:, 0].tolist()

    
    #In this code we want to properly adjust the table containing the power flow results, "net_bus_res_filtered", to account for the discarding     of the duplicate nodes. We only use this table to assign values/"measurements" to the quantities of the grid for the state estimation. In a real application, it will be useless.

    #From net_bus_res_filtered, we isolate the data corresponding to the buses of the switches. 
    net_bus_res_filtered=net.res_bus.copy()
    element_active_power=net_bus_res_filtered['p_mw'][buses_to_remove]
    element_reactive_power=net_bus_res_filtered['q_mvar'][buses_to_remove]
    bus_active_power=net_bus_res_filtered['p_mw'][buses_to_keep]
    bus_reactive_power=net_bus_res_filtered['q_mvar'][buses_to_keep]
    
    bus_active_power_array_indices=np.array(bus_active_power.index)
    bus_active_power_array_values=np.array(bus_active_power.values)
    element_active_power_array_indices=np.array(element_active_power.index)
    element_active_power_array_values=np.array(element_active_power.values)
    bus_active_power_array= np.column_stack((bus_active_power_array_indices, bus_active_power_array_values))
    element_active_power_array= np.column_stack((element_active_power_array_indices, element_active_power_array_values))
    
    bus_reactive_power_array_indices=np.array(bus_reactive_power.index)
    bus_reactive_power_array_values=np.array(bus_reactive_power.values)
    element_reactive_power_array_indices=np.array(element_reactive_power.index)
    element_reactive_power_array_values=np.array(element_reactive_power.values)
    bus_reactive_power_array= np.column_stack((bus_reactive_power_array_indices, bus_reactive_power_array_values))
    element_reactive_power_array= np.column_stack((element_reactive_power_array_indices, element_reactive_power_array_values))


    #The main concept here is the following: According to the convention of Pandapower, we have considered some buses to be original and others to be duplicates. The duplicates are to be discarded. Nevertheless, if the "duplicate" bus is an injection bus, then this injection has to be transferred to its corresponding original bus. If both the original bus and the duplicate bus are injection buses, then the actual injection at the equivalent node is their sum. So based on this we update the information regarding the active and the reactive power of the nodes between switches.
    updated_data_active_power = np.zeros((len(bus_active_power), 2))
    updated_data_active_power[:, 0] = bus_active_power_array[:, 0]

    for i in range(len(bus_active_power_array)):
        if bus_active_power_array[i, 1] == 0 and element_active_power_array[i, 1] == 0:
            updated_data_active_power[i, 1] = 0
        elif bus_active_power_array[i, 1] != 0 and element_active_power_array[i, 1] == 0:
            updated_data_active_power[i, 1] = bus_active_power_array[i, 1]
        elif bus_active_power_array[i, 1] == 0 and element_active_power_array[i, 1] != 0:
            updated_data_active_power[i, 1] = element_active_power_array[i, 1]
        else:
            updated_data_active_power[i, 1] = element_active_power_array[i, 1] + bus_active_power_array[i, 1]
            
    updated_data_reactive_power = np.zeros((len(bus_reactive_power), 2))
    updated_data_reactive_power[:, 0] = bus_reactive_power_array[:, 0]
    
    for i in range(len(bus_reactive_power_array)):
        if bus_reactive_power_array[i, 1] == 0 and element_reactive_power_array[i, 1] == 0:
            updated_data_reactive_power[i, 1] = 0
        elif bus_reactive_power_array[i, 1] != 0 and element_reactive_power_array[i, 1] == 0:
            updated_data_reactive_power[i, 1] = bus_reactive_power_array[i, 1]
        elif bus_reactive_power_array[i, 1] == 0 and element_reactive_power_array[i, 1] != 0:
            updated_data_reactive_power[i, 1] = element_reactive_power_array[i, 1]
        else:
            updated_data_reactive_power[i, 1] = element_reactive_power_array[i, 1] + bus_reactive_power_array[i, 1]  

    #Here's the update, using the auxiliary vectors
    net_bus_res_filtered.loc[buses_to_keep, 'p_mw'] = updated_data_active_power[:, 1]
    net_bus_res_filtered.loc[buses_to_keep, 'q_mvar'] = updated_data_reactive_power[:, 1]

    #After having correctly updated the power data, we get discard the duplicate buses
    net_bus_filtered = net.bus[~net.bus.index.isin(buses_to_remove)]
    net_bus_res_filtered=net_bus_res_filtered[~net.bus.index.isin(buses_to_remove)]
    
    #As a last step, we only keep the buses that are in service. Now, net_bus_filtered and net_bus_res_filtered contain the same buses that are considered by Pandapower
    net_bus_res_filtered=net_bus_res_filtered[net_bus_filtered['in_service']==True]
    net_bus_filtered = net_bus_filtered[net_bus_filtered['in_service']==True]

    #We insert a new column to make the mapping of the initial indices of the buses with new indices after the reduction
    net_bus_filtered.insert(0, 'real index', list(range(len(net_bus_filtered))))
    net_bus_res_filtered.insert(0, 'real index', list(range(len(net_bus_filtered))))

    #We also create a hashmap for this mapping
    hashmap_reduction = net_bus_filtered[['real index']].reset_index().set_index('real index').to_dict()['index']
    hashmap_reduction = {v: k for k, v in hashmap_reduction.items()}

    #Now we update the data regarding the transformers accordingly. These steps can be omitted, I've only included them for completeness
    net_trafo_updated=net.trafo.copy()
    buses_to_change_positions_hv = np.where(np.isin(net.trafo["hv_bus"].values, switch_hashmap.values[:,1]))
    counterparts_hv = np.where(np.isin(switch_hashmap.values[:,1], net.trafo["hv_bus"].values))
    net_trafo_updated["hv_bus"].values[buses_to_change_positions_hv]=switch_hashmap.values[counterparts_hv,0]

    buses_to_change_positions_lv = np.where(np.isin(net.trafo["lv_bus"].values, switch_hashmap.values[:,1]))
    counterparts_lv = np.where(np.isin(switch_hashmap.values[:,1], net.trafo["lv_bus"].values))
    net_trafo_updated["lv_bus"].values[buses_to_change_positions_lv]=switch_hashmap.values[counterparts_lv,0]

    indices_to_remove_trafo = np.where(np.isin(net_trafo_updated['hv_bus'].values, out_of_service_buses) | np.isin(net_trafo_updated['lv_bus'].values, out_of_service_buses))[0]
    net_trafo_updated = net_trafo_updated[~np.isin(np.arange(len(net_trafo_updated)), indices_to_remove_trafo)]

    
    net_trafo_updated.insert(3, 'real_index_hv', 0)
    # Map values from 'bus' column to 'real_index' column using hashmap_reduction
    for index, row in net_trafo_updated.iterrows():
        bus_value = row['hv_bus']
        if bus_value in hashmap_reduction:
            net_trafo_updated.at[index, 'real_index_hv'] = hashmap_reduction[bus_value]

    net_trafo_updated.insert(5, 'real_index_lv', 0)
    # Map values from 'bus' column to 'real_index' column using hashmap_reduction
    for index, row in net_trafo_updated.iterrows():
        bus_value = row['lv_bus']
        if bus_value in hashmap_reduction:
            net_trafo_updated.at[index, 'real_index_lv'] = hashmap_reduction[bus_value]

    #Here the same for the static generator data
    buses_to_change_positions_sgen = np.where(np.isin(net.sgen["bus"].values, switch_hashmap.values[:,1]))
    counterparts_sgen = np.where(np.isin(switch_hashmap.values[:,1], net.sgen["bus"].values))
    net_sgen_updated = net.sgen.copy()
    net_sgen_updated["bus"].values[buses_to_change_positions_sgen]=switch_hashmap.values[counterparts_sgen,0]
    indices_to_remove_sgen = np.where(np.isin(net_sgen_updated['bus'].values, out_of_service_buses))[0]
    net_sgen_updated = net_sgen_updated[~np.isin(np.arange(len(net_sgen_updated)), indices_to_remove_sgen)]
    
    net_sgen_updated.insert(2, 'real_index', 0)
    
    # Map values from 'bus' column to 'real_index' column using hashmap_reduction
    for index, row in net_sgen_updated.iterrows():
        bus_value = row['bus']
        if bus_value in hashmap_reduction:
            net_sgen_updated.at[index, 'real_index'] = hashmap_reduction[bus_value]

    #Here we update the zero_injection_buses set to remove duplicate nodes due to the switches
    for bus in zero_injection_buses:
        # Check if the bus is in switch_hashmap
        if bus in switch_hashmap['bus'].values:
            # Find the corresponding element
            corresponding_element = switch_hashmap.loc[switch_hashmap['bus'] == bus, 'element'].iloc[0]
            # Check if the corresponding element is in zero_injection_buses or injection_buses
            if corresponding_element in zero_injection_buses:
                # Remove corresponding element from zero_injection_buses (we only keep the original bus, we remove the duplicate) 
                zero_injection_buses = np.delete(zero_injection_buses, np.where(zero_injection_buses == corresponding_element))
            elif corresponding_element in injection_buses:
            # Remove bus from zero_injection_buses (this means that the original bus is not really a zero-injection bus, so we remove it) 
                zero_injection_buses = np.delete(zero_injection_buses, np.where(zero_injection_buses == bus))

    for bus in zero_injection_buses:
        # Check if the bus is in switch_hashmap
        if bus in switch_hashmap['element'].values:
            # Remove the element from zero_injection_buses
            zero_injection_buses = zero_injection_buses[zero_injection_buses != bus]
            

    #We also remove the out-of-service buses from the list
    indices_to_remove_zero_inj = np.where(np.isin(zero_injection_buses, out_of_service_buses))[0]
    zero_injection_buses = zero_injection_buses[~np.isin(np.arange(len(zero_injection_buses)), indices_to_remove_zero_inj)]

    #And we perform a mapping of the initial indices with the new ones
    for i in range(len(zero_injection_buses)):
        if zero_injection_buses[i] in hashmap_reduction:
            zero_injection_buses[i] = hashmap_reduction[zero_injection_buses[i]]
            
    #create a set with all buses of the network and one with the zero-injection ones
    net_bus_set = set(net_bus_res_filtered['real index'].values)
    zero_injection_bus_set = set(zero_injection_buses)        
    
    #find the buses of the network with injection as the difference between the previous sets
    injection_buses = net_bus_set - zero_injection_bus_set

    #convert the set into an array
    injection_buses = np.array(list(injection_buses))
    injection_buses = np.sort(injection_buses)
    
    lv_indices_pv = net_sgen_updated['real_index'].values

    # Initialize an array to store the mapped real_index_hv values
    hv_indices_pv = np.full(lv_indices_pv.shape, -1, dtype=int)

    for idx, real_index in enumerate(lv_indices_pv):
    # Find the row in net_trafo_updated where real_index_lv matches real_index
        trafo_row = net_trafo_updated[net_trafo_updated['real_index_lv'] == real_index]
        if not trafo_row.empty:
            real_index_hv = trafo_row.iloc[0]['real_index_hv']
            hv_indices_pv[idx] = real_index_hv
            
    hv_indices_pv=np.sort(hv_indices_pv)        

    #Here the update the slack bus, create a new hashmap to map the names of buses to their indices
    
    in_service_ext_grid = net.ext_grid[net.ext_grid['in_service']]
    slack_bus_initial = in_service_ext_grid.iloc[0]['bus']
    slack_bus=hashmap_reduction[slack_bus_initial]

    hashmap_names = net.bus[['name']].reset_index().set_index('name').to_dict()['index']

    #We also create the inverse dictionaries.
    hashmap_reduction2 = {value: key for key, value in hashmap_reduction.items()}
    hashmap_names2 = {value: key for key, value in hashmap_names.items()}


    #Stage 2: Extraction of the necessary hashmaps/adjacency matrices

    S_n=net._ppc['baseMVA']
    
   #We start by calculating the admittance matrix of the network
    Ybus = net._ppc['internal']['Ybus'].toarray()


    # Here we define and initialise the parent_sets and children_sets, i.e. the sets designating the parent bus and the children buses of each bus
    num_buses = len(Ybus)
    children_sets = np.zeros((num_buses, num_buses), dtype=int)
    parent_sets = np.zeros((num_buses, 2), dtype=int)
    children_sets[:, 0] = np.arange(num_buses)
    parent_sets[:, 0] = np.arange(num_buses)

    # We start from the slack_bus. We also create an auxiliary hashmap. This hashmap relates the actual indices of the buses with their indices, as appearing in the process of populating the parent_sets/ children_sets. So for example, the index of the slack bus might be 339, but it is the bus from which we start, so its new index is 0. This is mapped in the hashmap.
    slack_row = Ybus[slack_bus]
    children_indices = np.where((slack_row != 0) & (np.arange(num_buses) != slack_bus))[0]
    hashmap = np.zeros((num_buses, 2), dtype=int)
    hashmap[:, 0] = np.arange(num_buses)
    children_per_bus = np.zeros((num_buses, 2), dtype=int)
    children_per_bus[:, 0] = np.arange(num_buses)
    hashmap[0, 1] = slack_bus
    hashmap[1:1+len(children_indices), 1] = children_indices
    children_sets[0, 1:1+len(children_indices)] = children_indices
    parent_sets[1:1+len(children_indices), 1] = slack_bus
    counter = len(children_indices) + 1
    maximum_number_children = len(children_indices)
    children_per_bus[0, 1] = len(children_indices)

    #We also initialize array Y, that stores the admittance of each branch 
    Y = np.zeros(num_buses, dtype=complex)
   
    Y[children_indices]=-Ybus[slack_bus,children_indices]
    Y[slack_bus]=-1 #I want a nx1 array instead of a (n-1)x1 one, so I add "-1" value for the slack_bus position, even though no branch terminates at the slack bus

    # Process the other buses. Here I find the children of each bus, populate the sets, and extract the respective admittance
    for i in range(num_buses - 1):
        real_bus_index = hashmap[i+1, 1]
        bus_row = Ybus[real_bus_index]
        bus_children_indices = np.where((bus_row != 0) & (np.arange(num_buses) != real_bus_index) & (np.arange(num_buses) != parent_sets[i+1, 1]))[0]
        hashmap[counter:counter+len(bus_children_indices), 1] = bus_children_indices
        Y[bus_children_indices]=-Ybus[real_bus_index,bus_children_indices]
        children_sets[i+1, 1:1+len(bus_children_indices)] = bus_children_indices
        parent_sets[counter:counter+len(bus_children_indices), 1] = real_bus_index
        counter += len(bus_children_indices)
        children_per_bus[i + 1, :] = [i + 1, len(bus_children_indices)]
        maximum_number_children = max(maximum_number_children, len(bus_children_indices))

    Z=1/Y
    R=Z.real
    X=Z.imag

    #Same here regarding the (n-1) size
    R[slack_bus]=-1 
    X[slack_bus]=-1

    
    # Map indices to create children_sets_mapped and parent_sets_mapped. So here we just use the hashmap to obtain the actual sets of children and parent buses.
    children_sets_mapped = children_sets.copy()
    children_sets_mapped[:, 0] = hashmap[:, 1]
    parent_sets_mapped = parent_sets.copy()
    parent_sets_mapped[:, 0] = hashmap[:, 1]
    children_per_bus_mapped = children_per_bus
    children_per_bus_mapped[:, 0] = hashmap[:, 1]
    children_sets_mapped = np.delete(children_sets_mapped, np.s_[maximum_number_children+1:], axis=1)

    children_sets_mapped_new = children_sets_mapped.copy()

    for i in range(len(children_sets_mapped_new)):
        if children_per_bus[i, 1] < maximum_number_children:
            children_sets_mapped_new[i, children_per_bus[i, 1] + 1:] = -1

    rows, _ = children_sets_mapped_new.shape

    #The parent_child_matrix is a matrix that, for each bus, shows its parent and its children, if any
    parent_child_matrix = []

    for i in range(rows):
        # Find indices of elements in columns 1 to maximum_number_children that are not equal to -1
        valid_indices = np.where(children_sets_mapped_new[i, 1:maximum_number_children + 1] != -1)[0] + 1

        # Check if there are valid indices
        if valid_indices.size > 0:
            # Create new rows based on valid indices
            for j in valid_indices:
                new_row = [children_sets_mapped_new[i, 0], children_sets_mapped_new[i, j]]
                parent_child_matrix.append(new_row)

    parent_child_matrix = np.array(parent_child_matrix)

    parent_child_matrix_unmapped = np.zeros((num_buses - 1, 2), dtype=int)

    for i in range(num_buses - 1):
        parent_index_1 = np.where(hashmap[:, 1] == parent_child_matrix[i, 0])[0]
        parent_index_2 = np.where(hashmap[:, 1] == parent_child_matrix[i, 1])[0]

        parent_child_matrix_unmapped[i, 0] = hashmap[parent_index_1, 0] 
        parent_child_matrix_unmapped[i, 1] = hashmap[parent_index_2, 0] 


    all_buses_list = list(range(0, len(Ybus)))

    #Here I initialise the sets in order to start a backward sweep and, for each bus, determine the buses downstream of it. 
    all_downstream_sets = {bus: set() for bus in all_buses_list}
    all_downstream_branches_sets={bus: set() for bus in all_buses_list}


    # Backward sweep to determine downstream sets for all buses
    for bus in reversed(all_buses_list):
        # Find rows where the bus is the "from_bus" and identify the corresponding "to_bus"
        downstream_buses = set(parent_child_matrix_unmapped[parent_child_matrix_unmapped[:, 0] == bus][:, 1])
        downstream_branches= set(parent_child_matrix_unmapped[parent_child_matrix_unmapped[:, 0] == bus][:, 1])
        # Update downstream sets for the current bus
        all_downstream_sets[bus].update(downstream_buses)
        all_downstream_branches_sets[bus].update(downstream_branches)

        # Include the bus itself in the downstream set
        all_downstream_sets[bus].add(bus)

        # Update downstream sets for the current bus
        for downstream_bus in downstream_buses:
            all_downstream_sets[bus].update(all_downstream_sets[downstream_bus])

        for downstream_branch in downstream_branches:
            all_downstream_branches_sets[bus].update(all_downstream_branches_sets[downstream_branch])    

     # Here I do the same for the upstream buses of each bus, with a forward sweep
    all_upstream_sets = {bus: set() for bus in all_buses_list}
    all_upstream_branches_sets = {bus: set() for bus in all_buses_list}

    for bus in all_buses_list:
        # Find rows where the bus is the "to_bus" and identify the corresponding "from_bus"
        upstream_buses = set(parent_child_matrix_unmapped[parent_child_matrix_unmapped[:, 1] == bus][:, 0])
        upstream_branches = set(parent_child_matrix_unmapped[parent_child_matrix_unmapped[:, 1] == bus][:, 0])
    
        # Update upstream sets for the current bus
        all_upstream_sets[bus].update(upstream_buses)
        all_upstream_branches_sets[bus].update(upstream_branches)

        # Include the bus itself in the upstream set
        all_upstream_sets[bus].add(bus)
        all_upstream_branches_sets[bus].add(bus)

        # Update upstream sets for the current bus
        for upstream_bus in upstream_buses:
            all_upstream_sets[bus].update(all_upstream_sets[upstream_bus])

        for upstream_branch in upstream_branches:
            all_upstream_branches_sets[bus].update(all_upstream_branches_sets[upstream_branch])

    
    # Create a mapping dictionary from the left to the right column of the hashmap
    bus_mapping = dict(zip(hashmap[:, 0], hashmap[:, 1]))
    branch_mapping = dict(zip(hashmap[:, 0], hashmap[:, 1]))

    # Create a new dictionary to store unmapped downstream sets
    all_downstream_sets_unmapped = {bus_mapping[bus]: set() for bus in all_downstream_sets}
    all_downstream_branches_sets_unmapped={branch_mapping[branch]: set() for branch in all_downstream_branches_sets}

    all_upstream_sets_unmapped = {bus_mapping[bus]: set() for bus in all_upstream_sets}
    all_upstream_branches_sets_unmapped={branch_mapping[branch]: set() for branch in all_upstream_branches_sets}

    # Populate the unmapped downstream sets
    for bus, downstream_set in all_downstream_sets.items():
        unmapped_bus = bus_mapping[bus]
        unmapped_downstream_set = {bus_mapping[downstream_bus] for downstream_bus in downstream_set}
        all_downstream_sets_unmapped[unmapped_bus].update(unmapped_downstream_set)

    for branch, downstream_branch_set in all_downstream_branches_sets.items():
        unmapped_branch = branch_mapping[branch]
        unmapped_downstream_branch_set = {branch_mapping[downstream_branch] for downstream_branch in downstream_branch_set}
        all_downstream_branches_sets_unmapped[unmapped_branch].update(unmapped_downstream_branch_set)

   # Populate the unmapped upstream sets 
    for bus, upstream_set in all_upstream_sets.items():
        unmapped_bus = bus_mapping[bus]
        unmapped_upstream_set = {bus_mapping[upstream_bus] for upstream_bus in upstream_set}
        all_upstream_sets_unmapped[unmapped_bus].update(unmapped_upstream_set)

    for branch, upstream_branch_set in all_upstream_branches_sets.items():
        unmapped_branch = branch_mapping[branch]
        unmapped_upstream_branch_set = {branch_mapping[upstream_branch] for upstream_branch in upstream_branch_set}
        all_upstream_branches_sets_unmapped[unmapped_branch].update(unmapped_upstream_branch_set)
    

    # If we wanted to see the results printed 
    #for bus, downstream_set in all_downstream_sets_unmapped.items():
        #print(f"Unmapped Downstream set for Bus {bus}: {list(downstream_set)}")

    #for branch, downstream_branch_set in all_downstream_branches_sets_unmapped.items():
        #print(f"Unmapped Downstream branches set for Bus {branch}: {list(downstream_branch_set)}")    

    #We initialize the hashmaps (adjacency matrices) that show the buses and branches downstream of each bus
    adjacency_matrix_buses = np.zeros((num_buses, num_buses), dtype=int)
    adjacency_matrix_buses_upstream=np.zeros((num_buses, num_buses), dtype=int)

    #Adjacency matrix for downstream buses
    for bus, downstream_set in all_downstream_sets_unmapped.items():
        row_index = bus
        for downstream_bus in downstream_set:
            col_index = downstream_bus
            adjacency_matrix_buses[row_index, col_index] = 1

    #Adjacency matrix for upstream buses
    for bus, upstream_set in all_upstream_sets_unmapped.items():
        row_index = bus
        for upstream_bus in upstream_set:
            col_index = upstream_bus
            adjacency_matrix_buses_upstream[row_index, col_index] = 1

    #Adjacency matrix for downstream branches
    adjacency_matrix_branches = np.zeros((num_buses, num_buses), dtype=float) #I define it as (nxn) as well
    adjacency_matrix_branches[:, :slack_bus] = adjacency_matrix_buses[:, :slack_bus]
    adjacency_matrix_branches[:, slack_bus + 1:] = adjacency_matrix_buses[:, slack_bus+1:]

    np.fill_diagonal(adjacency_matrix_branches, 0)
    adjacency_matrix_branches[:, slack_bus] = -1

    #Adjacency matrix for upstream branches
    adjacency_matrix_branches_upstream = np.zeros((num_buses, num_buses), dtype=float) #I define it as (nxn) as well
    adjacency_matrix_branches_upstream[:, :slack_bus] = adjacency_matrix_buses_upstream[:, :slack_bus]
    adjacency_matrix_branches_upstream[:, slack_bus + 1:] = adjacency_matrix_buses_upstream[:, slack_bus+1:]

    adjacency_matrix_branches_upstream[:, slack_bus] = -1

    #Exclusion of slack bus
    adjacency_matrix_branches_no_slack = np.delete(adjacency_matrix_branches, slack_bus, axis=0) #This is the reduced version, as no branch terminating at the slack bus exists
    adjacency_matrix_branches_no_slack = np.delete(adjacency_matrix_branches_no_slack, slack_bus, axis=1)
    
    adjacency_matrix_branches_no_slack_upstream = np.delete(adjacency_matrix_buses_upstream, slack_bus, axis=0)  # Delete row
    adjacency_matrix_branches_no_slack_upstream = np.delete(adjacency_matrix_branches_no_slack_upstream, slack_bus, axis=1)  # Delete column

    #Here we correct the upstream branches sets by excluding the slack bus
    for key in all_upstream_branches_sets_unmapped:
        all_upstream_branches_sets_unmapped[key].discard(slack_bus)
    
    parent_child_adjacency = np.zeros((num_buses, num_buses), dtype=int)

    for i in range(num_buses):
        parent_index = parent_child_matrix[parent_child_matrix[:, 1] == i, 0]
        parent_child_adjacency[i, parent_index ] = 1

    downstream_upstream_matrix  = np.zeros_like(Ybus)
    non_zero_indices = np.nonzero(Ybus)
    downstream_upstream_matrix [non_zero_indices] = 1
    downstream_upstream_matrix=downstream_upstream_matrix.real
    downstream_upstream_matrix=(np.rint(downstream_upstream_matrix)).astype(int)


    #Stage 3: Here we calculate the sensitivity matrices of the equivalent DC model of the network. Eventually, we calculate the H matrix of the network
    R2=np.delete(R,slack_bus)
    X2=np.delete(X,slack_bus)

    R_matrix=np.zeros((len(R2), len(R2)))
    np.fill_diagonal(R_matrix,R2)
    X_matrix=np.zeros((len(X2),len(X2)))
    np.fill_diagonal(X_matrix,X2)

    adjacency_matrix_buses_no_slack = np.delete(adjacency_matrix_buses, slack_bus, axis=0)  # Delete row
    adjacency_matrix_buses_no_slack = np.delete(adjacency_matrix_buses_no_slack, slack_bus, axis=1)  # Delete column

    adjacency_matrix_buses_no_slack_transpose=np.transpose(adjacency_matrix_buses_no_slack)

    R_sensitivity=np.dot(np.dot(adjacency_matrix_buses_no_slack_transpose, R_matrix), adjacency_matrix_buses_no_slack)
    X_sensitivity=np.dot(np.dot(adjacency_matrix_buses_no_slack_transpose, X_matrix), adjacency_matrix_buses_no_slack)
    H_vp_full=-R_sensitivity
    H_vq_full=-X_sensitivity
     
    H_v_full=np.concatenate((H_vp_full, H_vq_full), axis=1)
   
    H_pp_full=np.eye(num_buses-1)
   
    H_pq_full=np.zeros((num_buses-1,num_buses-1))
   
    H_qq_full=np.eye(num_buses-1)
    
    H_qp_full=np.zeros((num_buses-1,num_buses-1))
    
    H_p_full=np.concatenate((H_pp_full,H_pq_full),axis=1)
    H_q_full=np.concatenate((H_qp_full,H_qq_full),axis=1)
    H_pq_full=np.concatenate((H_p_full,H_q_full),axis=0)

    slack_bus_row_ones=np.ones((1,H_pp_full.shape[1]))
    slack_bus_row_zeros=np.zeros((1,H_pp_full.shape[1]))
    
    slack_bus_row_P=np.concatenate((slack_bus_row_ones,slack_bus_row_zeros),axis=1)
    slack_bus_row_Q=np.concatenate((slack_bus_row_zeros,slack_bus_row_ones),axis=1)

    Yshunt=np.zeros(num_buses,dtype=complex)
    
    for aux in range(num_buses):
        non_zero_positions = np.argwhere(downstream_upstream_matrix[aux] != 0)
        Yshunt[aux]=np.sum(Ybus[aux,non_zero_positions])

    Gshunt=Yshunt.real
    Bshunt=Yshunt.imag

    #We obtain the ratings of the DER, to be used in the plausibility analysis
    der_positions_ratings = net_sgen_updated[['name','real_index', 'sn_mva']].reset_index().values
    der_positions_ratings=der_positions_ratings[:,2:4]
    
    der_positions_ratings=sorted(der_positions_ratings, key=lambda x: x[0])
    der_positions_ratings = np.array(der_positions_ratings)
    
    #Stage 3: We create Sets and Parameters in GAMSpy
    m=Container()
    i = Set(m, "i", description = "network nodes", records = [aux for aux in range(0,num_buses)])
    j=Alias(m,"j", alias_with=i)
    k=Alias(m,"k", alias_with=i)
    n=Alias(m,"n", alias_with=i)
    
    i2= Set(m,"i2",  description = "network nodes without slack bus/network branches", domain=i, records = [aux for aux in range(0,num_buses) if aux!=slack_bus])
    i3= Set(m,"i3",  description = "slack bus", domain=i, records = np.array([slack_bus]))
    
    hashmap_bus=Parameter(m,"hashmap_bus", domain=[i,j], records=adjacency_matrix_buses)
    hashmap_branch=Parameter(m,"hashmap_branch",domain=[i,k], records=adjacency_matrix_branches)
    hashmap_branch2=Parameter(m,"hashmap_branch2",domain=[i,k], records=adjacency_matrix_buses)
    hashmap_bus2=Parameter(m,"hashmap_bus2",domain=[i,j], records=adjacency_matrix_branches)
    hashmap_parent=Parameter(m,"hashmap_parent",domain=[i,n], records=parent_child_adjacency)
    #By default, Sb=100 MVA, while, for this case, Vb=20 kV. Therefore, Zb has been calculated as Zb=(Vb)^2/Sb=4 Ω.
    #Nevertheless, the bus injections are expressed in MWs and MVArs in the net.res_bus object. Therefore, their values correspond to pu values
    #considering an Sb'=1 MVA base value. In that case, we have Z'b=(Vb)^2/Sb'=400 Ω
    #Τherefore, if we consider an Sb'=1 MVA and use the injection values of "net.res_bus", we have to convert the impedance parameters to the new Zb'.
    #Zb/Z'b=1/100, that's why we divide by 100. In the case of coefficients, we multiply by 100, as they regard quantities measured in admittance units. 
    Rp=Parameter(m,"Rp", domain=i, records=R/S_n) 
    Xp=Parameter(m,"Xp", domain=i, records=X/S_n)
    Bp=Parameter(m,"Bp", domain=i, records=Bshunt*S_n)
    Gp=Parameter(m,"Gp", domain=i, records=Gshunt*S_n)
    
    return m,i,j,k,n,i2,i3,hashmap_bus, hashmap_branch, hashmap_parent, Rp,Xp,Gp,Bp, num_buses, slack_bus,der_positions_ratings,hashmap_names, hashmap_reduction, Ybus, Bshunt, Gshunt, hashmap_bus2, hashmap_branch2, zero_injection_buses, hashmap_reduction2, hashmap_names2,  H_v_full, H_p_full, H_q_full, slack_bus_row_P, slack_bus_row_Q, injection_buses
    
