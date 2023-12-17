x= linspace(-2,2,1000);

q = quantizer([5,5], 'ufixed', 'nearest');

y=quantize(q,x);

plot(x,y)
nb_quantization_levels = 2^(5);
% hold on
% 
% plot(0:1/nb_quantization_levels:1)
% hold off