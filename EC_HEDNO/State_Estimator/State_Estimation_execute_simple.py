import numpy as np
from gamspy import Set, Parameter, Variable, Equation, Model, Problem, Sense, Sum, math

def State_Estimation_execute(m, num_buses, mes_positions_p, mes_positions_q, mes_positions_v, mes_positions_pflow, 
                          mes_positions_qflow, zero_injection_buses, Pmes, Qmes, Vmes, Pflow_mes, Qflow_mes, slack_bus, Rp, Xp, Gp, Bp, hashmap_parent, hashmap_bus, hashmap_branch, hashmap_bus2, i, i2, i3, n, j, k, std_vector_p, std_vector_q, std_vector_v):
    
    mes_number_p = np.count_nonzero(mes_positions_p == 1)
    mes_number_q = np.count_nonzero(mes_positions_q == 1)
    mes_number_v = np.count_nonzero(mes_positions_v == 1)
    mes_number_pflow = np.count_nonzero(mes_positions_pflow == 1)
    mes_number_qflow = np.count_nonzero(mes_positions_qflow == 1)
             
    mes_p=Set(m,name="mes_p",domain=i,records=np.where(mes_positions_p==1)[0])
    mes_q=Set(m,name="mes_q",domain=i,records=np.where(mes_positions_q==1)[0])
    mes_v=Set(m,name="mes_v",domain=i,records=np.where(mes_positions_v==1)[0])
    mes_pflow=Set(m,name="mes_pflow", domain=i, records=np.where(mes_positions_pflow==1)[0])
    mes_qflow=Set(m,name="mes_qflow", domain=i, records=np.where(mes_positions_qflow==1)[0])
    
    Pmesp=Parameter(m, name="Pmesp",domain=i, records=Pmes)
    Qmesp=Parameter(m, name="Qmesp",domain=i, records=Qmes)
    Vmesp=Parameter(m, name="Vmesp",domain=i, records=Vmes)
    Pflow_mesp=Parameter(m, name="Pflow_mesp", domain=i, records=Pflow_mes)
    Qflow_mesp=Parameter(m, name="Qflow_mesp", domain=i, records=Qflow_mes)


    # Define zero injection buses
    if len(zero_injection_buses) > 0:
        i_zero = Set(m, name="i_zero", domain=i, records=[aux for aux in range(num_buses) if aux in zero_injection_buses])
    else:
        i_zero = Set(m, name="i_zero", domain=i, is_singleton=True)
    
    # Define standard deviation parameters
    Std_P = Parameter(m, name="Std_P", domain=i, records=std_vector_p)    
    Std_Q = Parameter(m, name="Std_Q", domain=i, records=std_vector_q)
    Std_V = Parameter(m, name="Std_V", domain=i, records=std_vector_v)

    # Define variables
    Jall = Variable(m, name = "Jall", description = "overall deviation")
    Vest = Variable(m, name="Vest", domain=i, description="voltage estimates", type="positive")
    Pest = Variable(m, name="Pest", domain=i, description="active power estimates")
    Qest = Variable(m, name="Qest", domain=i, description="reactive power estimates")
    Pest_t = Variable(m, name="Pest_t", domain=i, description="active power estimates with shunt")
    Qest_t = Variable(m, name="Qest_t", domain=i, description="reactive power estimates with shunt")
    Ploss_est = Variable(m, name="Ploss_est", domain=i, description="active power losses", type="positive")
    Qloss_est = Variable(m, name="Qloss_est", domain=i, description="reactive power losses", type="positive")
    Pflow_est = Variable(m, name="Pflow_est", domain=i, description="active power flow")
    Qflow_est = Variable(m, name="Qflow_est", domain=i, description="reactive power flow")

    # Set default values for variables
    Vest.l[i] = 1
    Ploss_est.l[i2] = 0.001
    Qloss_est.l[i2] = 0.001
    Vest.up[i] = 2
    Vest.lo[i] = 0.5
    Pest.l[mes_p[i]] = Pmesp[mes_p]
    Qest.l[mes_q[i]] = Qmesp[mes_q]
    Vest.l[mes_v[i]] = Vmesp[mes_v]

    # Define equations
    Deviation = Equation(m, name="Deviation")
    power_flow_eq2 = Equation(m, name="power_flow_eq2", domain=i)
    Ploss_calc = Equation(m, name="Ploss_calc", domain=i)
    Qloss_calc = Equation(m, name="Qloss_calc", domain=i)
    Pest_t_calc=Equation(m,name="Pest_t_calc", domain=i)
    Qest_t_calc=Equation(m,name="Qest_t_calc", domain=i)
    Pslack=Equation(m,name="Pslack",domain=i)
    Qslack=Equation(m,name="Qslack",domain=i)

    zero_injection_P=Equation(m,name="zero_injection_P", domain=i)
    zero_injection_Q=Equation(m,name="zero_injection_Q", domain=i)
    
    Deviation[...]=Jall==Sum(i.where[mes_p[i]],math.sqr(Pest[i]-Pmesp[i])/math.sqr(Std_P[i]))+Sum(i.where[mes_q[i]],math.sqr(Qest[i]-Qmesp[i])/math.sqr(Std_Q[i]))+Sum(i.where[mes_v[i]],math.sqr(Vest[i]-Vmesp[i])/math.sqr(Std_V[i]))
    
    power_flow_eq2[i].where[i2[i]] = Vest[i] == (math.sqrt(2)/2) * math.sqrt(
        math.sqr(Sum(n.where[hashmap_parent[i, n] == 1], Vest[n])) +
        2 * (
            (-Sum(j.where[hashmap_bus[i, j] == 1], Pest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Ploss_est[k])) * Rp[i] +
            (-Sum(j.where[hashmap_bus[i, j] == 1], Qest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Qloss_est[k])) * Xp[i]
        ) + math.sqrt(
            math.sqr(math.sqr(Sum(n.where[hashmap_parent[i, n] == 1], Vest[n]))) +
            4 * math.sqr(Sum(n.where[hashmap_parent[i, n] == 1], Vest[n])) *
            ((-Sum(j.where[hashmap_bus[i, j] == 1], Pest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Ploss_est[k])) * Rp[i] +
            (-Sum(j.where[hashmap_bus[i, j] == 1], Qest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Qloss_est[k])) * Xp[i]) -
            4 * math.sqr(
                (-Sum(j.where[hashmap_bus[i, j] == 1], Pest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Ploss_est[k])) * Xp[i] -
                (-Sum(j.where[hashmap_bus[i, j] == 1], Qest_t[j]) - Sum(k.where[hashmap_branch[i, k] == 1], Qloss_est[k])) * Rp[i]
            )
        )
    )
    
    Ploss_calc[i].where[i2[i]]=Ploss_est[i]==Rp[i]*(math.sqr(-Sum(j.where[hashmap_bus[i,j]==1],Pest_t[j])-Sum(k.where[hashmap_branch[i,k]==1],Ploss_est[k]))+math.sqr(-Sum(j.where[hashmap_bus[i,j]==1],Qest_t[j])-Sum(k.where[hashmap_branch[i,k]==1],Qloss_est[k])))/math.sqr(Vest[i])
    
    Qloss_calc[i].where[i2[i]]=Qloss_est[i]==Xp[i]*(math.sqr(-Sum(j.where[hashmap_bus[i,j]==1],Pest_t[j])-Sum(k.where[hashmap_branch[i,k]==1],Ploss_est[k]))+math.sqr(-Sum(j.where[hashmap_bus[i,j]==1],Qest_t[j])-Sum(k.where[hashmap_branch[i,k]==1],Qloss_est[k])))/math.sqr(Vest[i])


    Pest_t_calc[i].where[i2[i]]=Pest_t[i]==Pest[i]+Gp[i]*math.sqr(Vest[i])
    Qest_t_calc[i].where[i2[i]]=Qest_t[i]==Qest[i]-Bp[i]*math.sqr(Vest[i])

    #Pest_t_calc[i].where[i2[i]]=Pest_t[i]==Pest[i]
    #Qest_t_calc[i].where[i2[i]]=Qest_t[i]==Qest[i]
    
    Pslack[i].where[i3[i]]=Pest[i]==Sum(j.where[hashmap_bus2[i,j]==1],Pest_t[j])+Sum(k.where[hashmap_branch[i,k]==1],Ploss_est[k])+Gp[i]*math.sqr(Vest[i])
    Qslack[i].where[i3[i]]=Qest[i]==Sum(j.where[hashmap_bus2[i,j]==1],Qest_t[j])+Sum(k.where[hashmap_branch[i,k]==1],Qloss_est[k])-Bp[i]*math.sqr(Vest[i])
        
    
    zero_injection_P[i].where[i_zero[i]]=Pest[i]==0
    zero_injection_Q[i].where[i_zero[i]]=Qest[i]==0
    
    
    import sys
    estimation = Model(m, "estimation", equations=m.getEquations(), problem=Problem.NLP, sense=Sense.MIN, objective=Jall)
    estimation.solve(solver="CONOPT")

    return Vest, Pest, Qest, Vmesp, Pmesp, Qmesp, Std_V, Std_P, Std_Q, mes_v, mes_p, mes_q
    
