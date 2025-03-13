from State_Estimation_generic_function import State_Estimation_generic_function

# Define file paths and sheet names

#'data_filepath' is the path to the excel file 'EC_Network_reduced_merged.xlsx', which contains the representation of the network and it has been
#extracted from Powerfactory through the corresponding Pandapower extraction tool
#data_filepath = "C:\\Users\\stdim\\EC_Network_reduced_merged.xlsx"
data_filepath = "C:\\Users\\manba\\UNIVERSIDAD DE SEVILLA\\JOSE MARIA MAZA ORTEGA - cocoon-internal\\WP3\\Energy Community\\FDII Code_AUTH\\FDII Code_AUTH\\EC_Network_reduced_merged.xlsx"

#'measurement_filepath' contains the default, attack-free, input measurements/values. These values are categorized per physical quantity (voltage, active power, #and reactive power). Each bus is represented by its name in the Powerfactory file. Only the buses with active/reactive power injection are shown (i.e., the PV #buses and the slack bus), as for the zero-injection buses no measurement availability is assumed. 

#Replace the following paths with your actual paths

#measurement_filepath = "C:\\Users\\stdim\\George attacks\\Input measurements.xlsx"
measurement_filepath = "C:\\Users\\manba\\UNIVERSIDAD DE SEVILLA\\JOSE MARIA MAZA ORTEGA - cocoon-internal\\WP3\\Energy Community\\FDII Code_AUTH\\FDII Code_AUTH\\Input measurements.xlsx"
measurement_sheet_name = 'Measurements'  

# Execute the State Estimation function and unpack the results
(
     max_residual_measurement_type, max_residual_bus_index, max_residual_index, #     max_residual_val, Vest, Pest, Qest, Vmesp, Pmesp, Qmesp, 
     residuals_df_P, residuals_df_Q, residuals_df_V, removed_residuals
) =  State_Estimation_generic_function(
     data_filepath, measurement_filepath, measurement_sheet_name
)
a=1