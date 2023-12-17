% Function Name: segm_shift_binding
%
% Description: Shifts each segment of the left HV by the index of the
% segment of the right HV.
%
% Arguments:
%   A - left HV
%   B - right HV
%   D - hypervector dimension
%   p - probability of a 1
% 
% Returns:
%   binded_HV - resulting HV
% 

function binded_HV = segm_shift_binding(A, B, D, p)
    segm_length = floor(D*p);
    nb_of_segments = floor(1/p);
    binded_HV = zeros(1,D);
    for i = 0:nb_of_segments-1
        segment_A = A(i*segm_length+1:(i+1)*segm_length);
        segment_B = B(i*segm_length+1:(i+1)*segm_length);
        index_of_1_B = find(segment_B==1);
        segment_A = circshift(segment_A, index_of_1_B);
        binded_HV(i*segm_length+1:(i+1)*segm_length) = segment_A;
    end
end