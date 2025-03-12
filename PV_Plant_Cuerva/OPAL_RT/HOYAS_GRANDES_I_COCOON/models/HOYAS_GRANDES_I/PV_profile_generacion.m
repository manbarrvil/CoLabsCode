clear all
clc
load('generaciones_res_norm.mat');
[m,n]=size(generacion_norm);
load('DatosREDBT.mat');
time = data(1,1:n);

data_1=[time(1:450);-generacion_norm(1,151:end)];

% save('PV_prof_norm','data_1','-v4');