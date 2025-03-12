Po=1.887e3;
Uo=20e3;
Rfe=3*Uo^2/Po;
Pcc=21.96e3;
Ecc=0.06;
Sn=3e6;
Zcc=Ecc*Uo^2/Sn;
Icc=Sn/(sqrt(3)*Uo);
Rcc=Pcc/(3*Icc^2);
Xcc=sqrt(Zcc^2-Rcc^2);

%PU
Zb=Uo^2/Sn;
Rcc=Rcc/Zb;
Rfe=Rfe/Zb;
Xcc=Xcc/Zb;