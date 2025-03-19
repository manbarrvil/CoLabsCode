import numpy as np

def filter_measurements(Pmes, Qmes, der_positions_ratings):

    erroneous_p_indices = set()
    erroneous_q_indices = set()

    for row in der_positions_ratings:
        index = int(row[0])  # Index from the left column of der_ratings_positions
        threshold = row[1]   # Threshold value from the right column of der_ratings_positions

        # Check if the absolute value of the corresponding element in Pmes exceeds the threshold
        if abs(Pmes[index]) > threshold:
            erroneous_p_indices.add(index)  # Store the index for Pmes
        
        # Check if the absolute value of the corresponding element in Qmes exceeds the threshold
        if abs(Qmes[index]) > threshold:
            erroneous_q_indices.add(index)  # Store the index for Qmes
        
        # Check if sqrt(Pmes[index]**2 + Qmes[index]**2) exceeds the threshold
        if index not in erroneous_p_indices and index not in erroneous_q_indices:
            if np.sqrt(Pmes[index]**2 + Qmes[index]**2) > threshold:
                erroneous_p_indices.add(index)  # Store the index if not already added
                erroneous_q_indices.add(index)

    # Convert sets to sorted lists for consistent ordering
    erroneous_p_indices = sorted(erroneous_p_indices)
    erroneous_q_indices = sorted(erroneous_q_indices)

    erroneous_p_indices = np.array(erroneous_p_indices)
    erroneous_q_indices = np.array(erroneous_q_indices)
    
    # Remove erroneous indices from Pmes and Qmes
    #Pmes_filtered = np.delete(Pmes, erroneous_p_indices)
    #Qmes_filtered = np.delete(Qmes, erroneous_q_indices)

    return erroneous_p_indices, erroneous_q_indices



