% Function Name: gen_random_CIM
%
% Description: Generates a sparse random hypervector set that continuously
% grows less like the initial one.
%
% Arguments:
%   D - hypervector dimension
%   p - probability of a 1
%   nb_quantization_levels - number of HV's needed
%   nb_segments_to_change - number of different segments for the next HV
%   from the previous one
% 
% Returns:
%   CIM - continuous item memory generated
% 

function CIM = gen_random_CIM(D, p, nb_quantization_levels, nb_segments_to_change)

    if mod(D, 2)
        disp('Dimension is odd!!');
    else
        initial_HV = gen_random_HV_sparse_V2(D,p);
        nb_segments = floor(1/p);
        length_segment = floor(D*p);

        CIM = containers.Map ('KeyType','int32','ValueType','any');
        CIM(1) = initial_HV;
        %for every next HV, change a couple of segments
        for i = 2:nb_quantization_levels
            list_segments_to_change = randi([0,nb_segments-1], nb_segments_to_change);
            for j = 1:nb_segments_to_change
                rand_segment_index = randi([1,length_segment]);
                initial_HV(list_segments_to_change(j)*length_segment+1:(list_segments_to_change(j)+1)*length_segment) = zeros(1,length_segment);
                initial_HV(list_segments_to_change(j)*length_segment+rand_segment_index) = 1;
            end
            CIM(i) = initial_HV;
        end
    end
end