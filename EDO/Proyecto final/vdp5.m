function dydt = vdp5(t, y)
dydt = [36*(y(2) - y(1)); -y(1) * y(3) + 20*y(2); y(1)*y(2) - 3*y(3)];
end

%[appendix]{"version":"1.0"}
%---
