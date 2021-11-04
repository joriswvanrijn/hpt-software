function [on,off] = detectswitches(data)
% feed this fucntion a boolean vector (zeros and ones only). 
% if it contains a series of ones it will return the start and end position

% add zeros to beginning and end, such that ones at the beginning and end of
% the original data file get ercognized as such


data	= [4 data 4];


% find the transitions by using the shifting trick
data11	= data(1:end-1);
data12	= data(2:end);

numvect	= [1:1:length(data11)];

mdata	= data11 - data12;





    on.Fix=find(mdata == -1 | mdata == 3);                              % this is a sample to early
    off.Fix=find(mdata == 1 | mdata == -3);                                 % this is the correct one
    on.SP=find(mdata == 1 | mdata == 4);                                    % this is a sample to early
    off.SP=find(mdata == -1 | mdata == -4);                                    % this is the correct one

end
