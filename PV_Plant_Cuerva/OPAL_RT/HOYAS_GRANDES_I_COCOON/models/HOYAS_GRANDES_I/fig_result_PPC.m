load('Comunicaciones_sm_computation\OpREDHAWKtarget\myfile.mat');
[m,n]=size(opvar);
v_POI = [];
i_POI = [];
p_POI = [];
q_POI = [];
i=0;
t=opvar(1,:);
for k=2:4:13
    i=i+1;
    v_POI(i,:)=opvar(k,:);
    i_POI(i,:)=opvar(k+1,:);
    p_POI(i,:)=opvar(k+2,:);
    q_POI(i,:)=opvar(k+3,:);
end
rt=20e3/800;
P_CT1_ref=opvar(14,:);
P_CT2_ref=opvar(16,:);

% figure(1)
% plot(t,v_POI.*sqrt(3)/1e3)
% title('Tensiones de los POI')
% ylabel('Tensión [kV]')
% xlabel('Tiempo [s]')
% legend('CT1','CT2','POI')
% 
% figure(2)
% plot(t,i_POI)

figure(3)
plot(t,p_POI./1e3,t,P_CT1_ref,t,P_CT2_ref,t,P_CT1_ref+P_CT2_ref)
title('Potencias en los POI')
ylabel('Potencia activa [kW]')
xlabel('Tiempo [s]')
legend('CT1','CT2','POI','CT1_{ref}','CT2_{ref}','POI_{ref}')



