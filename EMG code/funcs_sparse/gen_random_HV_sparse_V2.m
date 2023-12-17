% Function Name: randomHV_sparse_V2
%
% Description: Generates a sparse random hypervector of 1's and 0's
%
% Arguments:
%   D - hypervector dimension
%   p - probability of a 1
% 
% Returns:
%   random_HV - generated random hypervector
% 

function random_HV = gen_random_HV_sparse_V2(D,p)

    if mod(D, 2)
        disp('Dimension is odd!!');
    else
        random_HV = zeros(1,D);
        length_segment = floor(D*p);
        for i = 0:(length_segment-1)
            rand_segment_index = randi([1,length_segment]);
            random_HV(i*length_segment+rand_segment_index) = 1;
        end
    end
end