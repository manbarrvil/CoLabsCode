def process_voltage_write_TagArray_Est (values):
    Vb_LV = 231
    Vb_MV = 20000

    values[0] = values[0]*Vb_MV
    values[1] = values[1]*Vb_MV
    values[2] = values[2]*Vb_MV
    values[3] = values[3]*Vb_LV
    values[4] = values[4]*Vb_MV
    values[5] = values[5]*Vb_MV
    values[6] = values[6]*Vb_MV
    values[7] = values[7]*Vb_LV
    values[8] = values[8]*Vb_MV
    values[9] = values[9]*Vb_MV
    values[10] = values[10]*Vb_LV
    values[11] = values[11]*Vb_MV
    values[12] = values[12]*Vb_MV
    values[13] = values[13]*Vb_LV
    values[14] = values[14]*Vb_MV
    values[15] = values[15]*Vb_LV
    values[16] = values[16]*Vb_MV
    values[17] = values[17]*Vb_MV
    values[18] = values[18]*Vb_LV
    values[19] = values[19]*Vb_MV
    values[20] = values[20]*Vb_MV
    values[21] = values[21]*Vb_MV
    values[22] = values[22]*Vb_LV
    values[23] = values[23]*Vb_MV
    values[24] = values[24]*Vb_LV
    values[25] = values[25]*Vb_MV
    values[26] = values[26]*Vb_MV
    values[27] = values[27]*Vb_LV
    
    return values